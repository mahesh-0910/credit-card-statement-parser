"""
Comprehensive test script for all bank statements
"""
import os
from parser import parse_credit_card_statement

def test_all_statements():
    """Test all generated statements"""
    
    # Expected data for validation
    expected_data = {
        "ICICI_Statement_7823.pdf": {
            "bank": "ICICI",
            "card_last4": "7823",
            "total_due": "42,105",
            "credit_limit": "500,000"
        },
        "HDFC_Statement_4589.pdf": {
            "bank": "HDFC",
            "card_last4": "4589",
            "total_due": "67,533",
            "credit_limit": "150,000"
        },
        "Axis_Statement_9012.pdf": {
            "bank": "AXIS",
            "card_last4": "9012",
            "total_due": "22,955",
            "credit_limit": "500,000"
        },
        "SBI_Statement_3456.pdf": {
            "bank": "SBI",
            "card_last4": "3456",
            "total_due": "72,225",
            "credit_limit": "300,000"
        },
        "Kotak_Statement_6789.pdf": {
            "bank": "KOTAK",
            "card_last4": "6789",
            "total_due": "70,487",
            "credit_limit": "150,000"
        }
    }
    
    print("\n" + "="*80)
    print("CREDIT CARD STATEMENT PARSER - COMPREHENSIVE TEST")
    print("="*80 + "\n")
    
    total_tests = 0
    passed_tests = 0
    failed_banks = []
    
    for statement_file, expected in expected_data.items():
        if os.path.exists(statement_file):
            total_tests += 1
            print(f"\n{'='*80}")
            print(f"📄 Testing: {statement_file}")
            print(f"{'='*80}")
            
            result = parse_credit_card_statement(statement_file)
            
            # Display results
            print(f"\n🏦 Bank:           {result['bank']}")
            print(f"💳 Card Number:    {result['card_number']}")
            print(f"📅 Statement Date: {result['statement_date']}")
            print(f"💰 Total Due:      {result['total_due']}")
            print(f"⏰ Due Date:       {result['due_date']}")
            print(f"🎯 Credit Limit:   {result['credit_limit']}")
            
            # Validate results
            errors = []
            
            if result['bank'] != expected['bank']:
                errors.append(f"Bank mismatch: expected {expected['bank']}, got {result['bank']}")
            
            if expected['card_last4'] not in result['card_number']:
                errors.append(f"Card number wrong: expected ****{expected['card_last4']}, got {result['card_number']}")
            
            if result['total_due'] == "Not Found":
                errors.append(f"Total due not found (expected ₹{expected['total_due']})")
            elif expected['total_due'] not in result['total_due']:
                errors.append(f"Total due mismatch: expected ₹{expected['total_due']}, got {result['total_due']}")
            
            if result['credit_limit'] == "Not Found":
                errors.append(f"Credit limit not found (expected ₹{expected['credit_limit']})")
            elif expected['credit_limit'] not in result['credit_limit']:
                errors.append(f"Credit limit mismatch: expected ₹{expected['credit_limit']}, got {result['credit_limit']}")
            
            if result['due_date'] == "Not Found":
                errors.append("Due date not found")
            
            if result['statement_date'] == "Not Found":
                errors.append("Statement date not found")
            
            # Print validation results
            if errors:
                print(f"\n❌ TEST FAILED - {len(errors)} issues:")
                for error in errors:
                    print(f"   • {error}")
                failed_banks.append(expected['bank'])
            else:
                print(f"\n✅ TEST PASSED - All fields extracted correctly!")
                passed_tests += 1
                
        else:
            print(f"\n❌ File not found: {statement_file}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    
    if failed_banks:
        print(f"\nFailed Banks: {', '.join(failed_banks)}")
    else:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
    
    print("="*80 + "\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_all_statements()
    exit(0 if success else 1)
