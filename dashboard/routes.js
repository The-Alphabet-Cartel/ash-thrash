/**
 * Testing Routes for Ash-Dash Integration
 * 
 * This file provides Express.js routes for integrating ash-thrash testing
 * results with the ash-dash analytics dashboard.
 * 
 * Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
 * Discord: https://discord.gg/alphabetcartel
 */

const express = require('express');
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const router = express.Router();

// Configuration
const ASH_THRASH_API = process.env.ASH_THRASH_API || 'http://10.20.30.16:8884';
const RESULTS_CACHE_TTL = 60000; // 1 minute cache

// Cache for results to reduce API calls
let resultsCache = {
    data: null,
    timestamp: 0
};

/**
 * Get current testing status and metrics
 * GET /api/testing/status
 */
router.get('/status', async (req, res) => {
    try {
        // Check cache first
        const now = Date.now();
        if (resultsCache.data && (now - resultsCache.timestamp) < RESULTS_CACHE_TTL) {
            return res.json({
                success: true,
                cached: true,
                data: resultsCache.data
            });
        }

        // Fetch fresh data from ash-thrash API
        const response = await axios.get(`${ASH_THRASH_API}/api/test/status`, {
            timeout: 5000
        });

        const testingData = response.data;

        // Transform data for dashboard consumption
        const dashboardData = {
            timestamp: new Date().toISOString(),
            testing_status: {
                overall_health: testingData.overall_health || 'unknown',
                last_test_time: testingData.last_test_time,
                next_scheduled_test: testingData.next_scheduled_test,
                total_tests_today: testingData.total_tests_today || 0
            },
            metrics: {
                overall_pass_rate: testingData.overall_pass_rate || 0,
                goal_achievement_rate: testingData.goal_achievement_rate || 0,
                avg_response_time: testingData.avg_response_time || 0,
                tests_passed: testingData.tests_passed || 0,
                tests_failed: testingData.tests_failed || 0,
                total_tests: testingData.total_tests || 0
            },
            categories: testingData.category_results || {},
            alerts: testingData.alerts || [],
            performance: {
                cpu_usage: testingData.cpu_usage || 0,
                memory_usage: testingData.memory_usage || 0,
                api_latency: testingData.api_latency || 0
            }
        };

        // Update cache
        resultsCache = {
            data: dashboardData,
            timestamp: now
        };

        res.json({
            success: true,
            cached: false,
            data: dashboardData
        });

    } catch (error) {
        console.error('Error fetching testing status:', error.message);
        
        // Return cached data if available, otherwise error
        if (resultsCache.data) {
            return res.json({
                success: true,
                cached: true,
                warning: 'Using cached data due to API error',
                data: resultsCache.data
            });
        }

        res.status(500).json({
            success: false,
            error: 'Failed to fetch testing status',
            message: error.message
        });
    }
});

/**
 * Get detailed test results
 * GET /api/testing/results
 */
router.get('/results', async (req, res) => {
    try {
        const { limit = 10, category = null } = req.query;
        
        const response = await axios.get(`${ASH_THRASH_API}/api/test/results`, {
            params: { limit, category },
            timeout: 10000
        });

        res.json({
            success: true,
            data: response.data
        });

    } catch (error) {
        console.error('Error fetching test results:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch test results',
            message: error.message
        });
    }
});

/**
 * Trigger a new test run
 * POST /api/testing/trigger
 */
router.post('/trigger', async (req, res) => {
    try {
        const { test_type = 'quick' } = req.body;
        
        const response = await axios.post(`${ASH_THRASH_API}/api/test/trigger`, {
            test_type,
            triggered_by: 'dashboard',
            timestamp: new Date().toISOString()
        }, {
            timeout: 30000
        });

        // Clear cache to force fresh data on next request
        resultsCache.data = null;

        res.json({
            success: true,
            message: `${test_type} test triggered successfully`,
            test_id: response.data.test_id,
            estimated_duration: response.data.estimated_duration
        });

    } catch (error) {
        console.error('Error triggering test:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to trigger test',
            message: error.message
        });
    }
});

/**
 * Get testing goals and achievement status
 * GET /api/testing/goals
 */
router.get('/goals', async (req, res) => {
    try {
        const response = await axios.get(`${ASH_THRASH_API}/api/test/goals`, {
            timeout: 5000
        });

        const goalsData = response.data;

        // Transform for dashboard display
        const dashboardGoals = {
            summary: goalsData.summary || {},
            categories: Object.entries(goalsData.categories || {}).map(([key, goal]) => ({
                id: key,
                name: goal.display_name || key.replace('_', ' ').toUpperCase(),
                target: goal.target_pass_rate || 0,
                current: goal.current_pass_rate || 0,
                achieved: goal.goal_met || false,
                trend: goal.trend || 'stable',
                last_updated: goal.last_updated
            })),
            overall_achievement: goalsData.achievement_rate || 0
        };

        res.json({
            success: true,
            data: dashboardGoals
        });

    } catch (error) {
        console.error('Error fetching testing goals:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch testing goals',
            message: error.message
        });
    }
});

/**
 * Get historical performance trends
 * GET /api/testing/trends
 */
router.get('/trends', async (req, res) => {
    try {
        const { days = 7, metric = 'pass_rate' } = req.query;
        
        const response = await axios.get(`${ASH_THRASH_API}/api/test/trends`, {
            params: { days, metric },
            timeout: 10000
        });

        res.json({
            success: true,
            data: response.data
        });

    } catch (error) {
        console.error('Error fetching trends:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch trends data',
            message: error.message
        });
    }
});

/**
 * Health check for testing integration
 * GET /api/testing/health
 */
router.get('/health', async (req, res) => {
    try {
        const response = await axios.get(`${ASH_THRASH_API}/health`, {
            timeout: 3000
        });

        res.json({
            success: true,
            ash_thrash_status: 'healthy',
            integration_status: 'operational',
            cache_status: resultsCache.data ? 'populated' : 'empty',
            last_cache_update: new Date(resultsCache.timestamp).toISOString()
        });

    } catch (error) {
        res.status(503).json({
            success: false,
            ash_thrash_status: 'unhealthy',
            integration_status: 'degraded',
            error: error.message
        });
    }
});

/**
 * Clear results cache (for debugging/admin)
 * POST /api/testing/cache/clear
 */
router.post('/cache/clear', (req, res) => {
    resultsCache = {
        data: null,
        timestamp: 0
    };

    res.json({
        success: true,
        message: 'Results cache cleared successfully'
    });
});

module.exports = router;