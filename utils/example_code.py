"""
Contains a default example of Python code to be used in the application.

This provides a quick way for users to test the functionality without
having to provide their own code immediately. The chosen example is
intentionally inefficient and poorly styled to better showcase the
Refactor and Optimize features.
"""

EXAMPLE_CODE = """
import time

# Function to find common elements between two lists, written inefficiently
def find_common_elements(list1, list2):
    common_elements = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                if item1 not in common_elements:
                    common_elements.append(item1)
    return common_elements

# A simple class example
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        # Pretend to do some processing
        print("Processing data...")
        time.sleep(1)
        # A simple transformation
        transformed_data = [x * 2 for x in self.data]
        return transformed_data

if __name__ == '__main__':
    list_a = [i for i in range(1000)]
    list_b = [i for i in range(500, 1500)]
    
    start_time = time.time()
    result = find_common_elements(list_a, list_b)
    end_time = time.time()
    
    print(f"Found {len(result)} common elements.")
    print(f"Inefficient execution time: {end_time - start_time:.4f} seconds")

    processor = DataProcessor([1, 2, 3, 4, 5])
    processed = processor.process()
    print("Processed data:", processed)
"""
