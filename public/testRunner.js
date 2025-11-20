// Simple test runner for browser console
console.log('🧪 Running Winter Break Tests...\n');

// Test 1: Winter break logic
console.log('1️⃣ Testing Winter Break Date Logic:');
testWinterBreakLogic();

// Test 2: Project-level restrictions  
setTimeout(() => {
  console.log('\n2️⃣ Testing Project-Level Restrictions:');
  testProjectLevelWinterBreak();
}, 100);

console.log('\n✅ All tests completed! Check results above.');