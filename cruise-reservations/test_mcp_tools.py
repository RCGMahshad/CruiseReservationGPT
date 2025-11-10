"""
Test script for MCP server tools

This script allows you to test each MCP tool individually without running the full server.
"""

import asyncio
import sys
from pathlib import Path

# Import the actual MCP tool functions from mcp_server
from mcp_server import get_ship_descriptions, get_cruise_itineraries, reserve_cruise


async def test_get_royal_caribbean_ship_descriptions(query: str = "luxury dining", max_results: int = 5):
    """Test the ship descriptions search tool."""
    print("\n" + "="*80)
    print("TEST: get_royal_caribbean_ship_descriptions")
    print("="*80)
    print(f"Query: {query}")
    print(f"Max Results: {max_results}")
    print("-"*80)
    
    try:
        # Call the actual MCP tool function
        result = await get_ship_descriptions(query, max_results)
        
        print("\n✅ RESULT:\n")
        print(result)
        print("\n" + "-"*80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def test_get_royal_caribbean_cruise_itineraries():
    """Test the cruise itineraries tool."""
    print("\n" + "="*80)
    print("TEST: get_royal_caribbean_cruise_itineraries")
    print("="*80)
    
    try:
        # Call the actual MCP tool function
        result = await get_cruise_itineraries()
        
        print("\n✅ RESULT:\n")
        print(result)
        print("\n" + "-"*80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def test_reserve_cruise(email: str = "test@example.com", 
                              first_name: str = "John", 
                              last_name: str = "Doe",
                              ship: str = "Harmony of the Seas",
                              sail_date: str = "2024-12-15",
                              cabin_type: str = "Balcony",
                              num_travelers: int = 2,
                              price: float = 1299.99):
    """Test the cruise reservation tool."""
    
    try:
        # Call the actual MCP tool function
        result = await reserve_cruise(email, first_name, last_name, ship, sail_date, cabin_type, num_travelers, price)
        
        print("\n✅ RESULT:\n")
        print(result)
        print("\n" + "-"*80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def run_all_tests():
    """Run all tests."""
    print("\n" + "🚢"*40)
    print("MCP TOOLS TEST SUITE")
    print("🚢"*40)
    
    # Test 1: Ship descriptions with default query
    await test_get_royal_caribbean_ship_descriptions(query="luxury dining options", max_results=3)
    
    # Test 2: Ship descriptions with different query
    await test_get_royal_caribbean_ship_descriptions(query="family activities", max_results=2)
    
    # Test 3: Cruise itineraries
    await test_get_royal_caribbean_cruise_itineraries()
    
    # Test 4: Reserve cruise
    await test_reserve_cruise()
    
    print("\n" + "🚢"*40)
    print("TESTS COMPLETED")
    print("🚢"*40 + "\n")


def main():
    """Main function with menu."""
    print("\n" + "="*80)
    print("MCP TOOLS TESTER")
    print("="*80)
    print("\nSelect a test to run:")
    print("  1. Test ship descriptions search (luxury dining)")
    print("  2. Test ship descriptions search (family activities)")
    print("  3. Test ship descriptions search (custom query)")
    print("  4. Test cruise itineraries")
    print("  5. Test cruise reservation")
    print("  6. Test cruise reservation (custom details)")
    print("  7. Run all tests")
    print("  8. Exit")
    print("-"*80)
    
    choice = input("\nEnter your choice (1-8): ").strip()
    
    if choice == "1":
        asyncio.run(test_get_royal_caribbean_ship_descriptions("luxury dining options", 3))
    elif choice == "2":
        asyncio.run(test_get_royal_caribbean_ship_descriptions("family activities", 3))
    elif choice == "3":
        query = input("Enter your search query: ").strip()
        max_results = input("Enter max results (default 5): ").strip()
        max_results = int(max_results) if max_results else 5
        asyncio.run(test_get_royal_caribbean_ship_descriptions(query, max_results))
    elif choice == "4":
        asyncio.run(test_get_royal_caribbean_cruise_itineraries())
    elif choice == "5":
        asyncio.run(test_reserve_cruise())
    elif choice == "6":
        print("\n" + "-"*80)
        email = input("Enter email: ").strip()
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        ship = input("Enter ship name: ").strip()
        sail_date = input("Enter sail date (YYYY-MM-DD): ").strip()
        cabin_type = input("Enter cabin type: ").strip()
        num_travelers = int(input("Enter number of travelers: ").strip())
        price = float(input("Enter price per person: ").strip())
        asyncio.run(test_reserve_cruise(email, first_name, last_name, ship, sail_date, cabin_type, num_travelers, price))
    elif choice == "7":
        asyncio.run(run_all_tests())
    elif choice == "8":
        print("\nExiting...")
        return
    else:
        print("\n❌ Invalid choice. Please try again.")
        main()
    
    # Ask if user wants to run more tests
    print("\n" + "-"*80)
    again = input("\nRun another test? (y/n): ").strip().lower()
    if again == 'y':
        main()
    else:
        print("\nGoodbye! 🚢\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Exiting...\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
