import { enhancedApiService } from '../src/services/enhancedApi';

// Test script to verify the enhanced API service and error handling
async function testErrorHandling() {
  console.log('Testing Enhanced API Service and Error Handling...\n');

  // Test 1: Network timeout
  console.log('Test 1: Network timeout simulation');
  try {
    await enhancedApiService.request('/test-timeout', { 
      method: 'GET',
      timeout: 1000 // Very short timeout
    });
  } catch (error) {
    console.log('✓ Timeout error caught:', error.message);
    console.log('  Error type:', error.type);
  }

  // Test 2: Invalid endpoint (404)
  console.log('\nTest 2: Invalid endpoint (404)');
  try {
    await enhancedApiService.request('/nonexistent-endpoint', { 
      method: 'GET'
    });
  } catch (error) {
    console.log('✓ 404 error caught:', error.message);
    console.log('  Error type:', error.type);
    console.log('  Status:', error.status);
  }

  // Test 3: Safe request wrapper
  console.log('\nTest 3: Safe request wrapper');
  const result = await enhancedApiService.safeRequest('/another-nonexistent');
  if (result.error) {
    console.log('✓ Safe request error handled:', result.error);
  }

  // Test 4: Retry mechanism
  console.log('\nTest 4: Retry mechanism');
  try {
    await enhancedApiService.request('/unstable-endpoint', { 
      method: 'GET',
      retries: 3
    });
  } catch (error) {
    console.log('✓ Final error after retries:', error.message);
  }

  console.log('\n✅ All error handling tests completed!');
}

// Run the test if this file is executed directly
if (typeof window === 'undefined') {
  testErrorHandling().catch(console.error);
}

export { testErrorHandling };
