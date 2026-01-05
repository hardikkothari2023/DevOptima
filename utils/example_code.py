"""
Default example code to be loaded into the editor.
Designed to demonstrate:
1. Simulation (State changes in loop)
2. Refactoring (Poor style)
3. Optimization (Inefficient string concat)
"""

EXAMPLE_CODE = """def process_orders(orders_list):
    # This function is messy and needs refactoring
    total = 0
    receipts = []
    
    for o in orders_list:
        if o['price'] > 100:
            # Expensive item
            disc = o['price'] * 0.9
        else:
            disc = o['price']
            
        total = total + disc
        
        # Inefficient string concatenation
        r_id = "REC-" + str(o['id']) + "-" + str(int(disc))
        receipts.append(r_id)
        
    return total, receipts

# Test Data
data = [
    {'id': 101, 'price': 50},
    {'id': 102, 'price': 150},
    {'id': 103, 'price': 20}
]

t, r = process_orders(data)
print(f"Final Total: {t}")
print(f"Receipts: {r}")
"""