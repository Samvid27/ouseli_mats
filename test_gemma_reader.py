
from ingest.gemma_reader import extract_transactions


fictional_statement = """
UPI TRANSACTION HISTORY
20-10-2026  Swiggy     Paid Rs. 420.00
20-10-2026  Netflix    Paid Rs. 649.00
21-10-2026  Salary     Received Rs. 25000.00
"""

result = extract_transactions(source_text=fictional_statement)

print("Provider:", result["provider"])
print("Document type:", result["doc_type"])
print("Extracted transactions:")

for row in result["rows"]:
    print(row)
