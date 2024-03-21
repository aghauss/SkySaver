import csv

def compare_csv_files(file1_path, file2_path):
    with open(file1_path, 'r', newline='', encoding='utf-8') as file1, \
         open(file2_path, 'r', newline='', encoding='utf-8') as file2:
        
        reader1 = csv.reader(file1)
        reader2 = csv.reader(file2)
        
        discrepancy_count = 0
        row_num = 1
        
        for row1, row2 in zip(reader1, reader2):
            if row1 != row2:
                discrepancy_count += 1
                print(f"Discrepancy found at row {row_num}:")
                print(f"File 1: {row1}")
                print(f"File 2: {row2}")
                # Uncomment the next line if you want to stop at the first discrepancy
                # break
            row_num += 1

        if discrepancy_count == 0:
            print("The files are identical.")
        else:
            print(f"Total discrepancies found: {discrepancy_count}")

# Example usage
file1 = '../data/4.processed_data/Processed_Query_1502.csv'
file2 = '../data/4.processed_data/Query_1502_processed.csv'
compare_csv_files(file1, file2)

