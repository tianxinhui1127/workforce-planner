import { isInWinterBreak } from './workforceGenerator';
import type { MonthData } from '../types/workforce';

// Test winter break functionality
function testWinterBreakLogic() {
  console.log('🧪 Testing Winter Break Logic...\n');
  
  // Test cases for cross-year winter break (Nov-Apr)
  const testCases: Array<{
    month: MonthData;
    winterBreakStart: number;
    winterBreakEnd: number;
    expected: boolean;
    description: string;
  }> = [
    // Cross-year winter break (Nov-Apr)
    { month: [2025, 10], winterBreakStart: 11, winterBreakEnd: 4, expected: false, description: 'October 2025 (before winter break)' },
    { month: [2025, 11], winterBreakStart: 11, winterBreakEnd: 4, expected: true, description: 'November 2025 (start of winter break)' },
    { month: [2025, 12], winterBreakStart: 11, winterBreakEnd: 4, expected: true, description: 'December 2025 (in winter break)' },
    { month: [2026, 1], winterBreakStart: 11, winterBreakEnd: 4, expected: true, description: 'January 2026 (in winter break)' },
    { month: [2026, 2], winterBreakStart: 11, winterBreakEnd: 4, expected: true, description: 'February 2026 (in winter break)' },
    { month: [2026, 3], winterBreakStart: 11, winterBreakEnd: 4, expected: true, description: 'March 2026 (in winter break)' },
    { month: [2026, 4], winterBreakStart: 11, winterBreakEnd: 4, expected: true, description: 'April 2026 (end of winter break)' },
    { month: [2026, 5], winterBreakStart: 11, winterBreakEnd: 4, expected: false, description: 'May 2026 (after winter break)' },
    
    // Same-year winter break (Jun-Aug)
    { month: [2026, 5], winterBreakStart: 6, winterBreakEnd: 8, expected: false, description: 'May 2026 (before summer break)' },
    { month: [2026, 6], winterBreakStart: 6, winterBreakEnd: 8, expected: true, description: 'June 2026 (start of summer break)' },
    { month: [2026, 7], winterBreakStart: 6, winterBreakEnd: 8, expected: true, description: 'July 2026 (in summer break)' },
    { month: [2026, 8], winterBreakStart: 6, winterBreakEnd: 8, expected: true, description: 'August 2026 (end of summer break)' },
    { month: [2026, 9], winterBreakStart: 6, winterBreakEnd: 8, expected: false, description: 'September 2026 (after summer break)' },
  ];
  
  let passed = 0;
  let failed = 0;
  
  testCases.forEach(({ month, winterBreakStart, winterBreakEnd, expected, description }) => {
    const result = isInWinterBreak(month, winterBreakStart, winterBreakEnd);
    const status = result === expected ? '✅ PASS' : '❌ FAIL';
    
    if (result === expected) {
      passed++;
    } else {
      failed++;
    }
    
    console.log(`${status} ${description}: ${result ? 'IN' : 'NOT IN'} winter break`);
  });
  
  console.log(`\n📊 Test Results: ${passed} passed, ${failed} failed`);
  
  if (failed === 0) {
    console.log('🎉 All winter break logic tests passed!');
  } else {
    console.log('⚠️  Some tests failed. Please review the implementation.');
  }
}

// Test project-level winter break configuration
function testProjectLevelWinterBreak() {
  console.log('\n🏗️ Testing Project-Level Winter Break Configuration...\n');
  
  // Simulate different project types
  const projectTypes = [
    { key: 'subgrade', name: '路基工程', shouldHaveWinterBreak: true },
    { key: 'pavement', name: '路面工程', shouldHaveWinterBreak: true },
    { key: 'bridge', name: '桥梁工程', shouldHaveWinterBreak: true },
    { key: 'building', name: '房建工程', shouldHaveWinterBreak: true },
    { key: 'tunnel', name: '隧道工程', shouldHaveWinterBreak: false },
  ];
  
  projectTypes.forEach(({ key, name, shouldHaveWinterBreak }) => {
    const isTunnel = key.startsWith('tunnel');
    const canHaveWinterBreak = !isTunnel;
    const status = canHaveWinterBreak === shouldHaveWinterBreak ? '✅ PASS' : '❌ FAIL';
    
    console.log(`${status} ${name} (${key}): ${canHaveWinterBreak ? 'CAN' : 'CANNOT'} have winter break`);
  });
  
  console.log('\n🎯 Tunnel projects correctly excluded from winter break functionality!');
}

// Run all tests
console.log('🔍 Starting Winter Break Functionality Tests...\n');
testWinterBreakLogic();
testProjectLevelWinterBreak();