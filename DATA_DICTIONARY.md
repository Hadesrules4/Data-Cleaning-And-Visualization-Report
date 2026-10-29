# Data Dictionary

| Column | Meaning | Cleaning rule |
|---|---|---|
| order_id | Order identifier | Preserved as supplied |
| order_date | Order date | Parsed as date; invalid dates removed |
| product | Product category | Missing values filled with mode |
| region | Sales region | Missing values filled with mode |
| sales_channel | Purchase channel | Missing values filled with mode |
| quantity | Units in order | Non-positive/outlier values handled; median imputation |
| unit_price | Unit price in INR | Non-positive/outlier values handled; median imputation |
| customer_rating | Rating from 1 to 5 | Invalid/outlier values handled; median imputation |
| sales | Order revenue in INR | Recalculated as quantity × unit price |
