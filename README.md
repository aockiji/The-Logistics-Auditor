
## Executive Summary
This audit of Veridi Logistics' delivery data reveals that the CEO's concern about inaccurate estimates is only partially supported. 

Although the majority of orders arrive on time or early, a significant regional problem exists such that the northeastern states like AL, MA, and SE have late delivery rates of 12-21% which is more than double the national average of 6.8%. 

Also, late deliveries directly correlate with lower review scores, with 4.3 stars for on-time orders dropping to below 2 for super late ones. 

## Project Links
- **Notebook:** [Google Colab link](https://colab.research.google.com/drive/1kXYvdeAXC0vekKvWwVp4d3odnQ4_FuNm?usp=sharing)
- **Dashboard:** [Streamlit link](https://the-logistics-auditor-k5bgkcamm8akshyzp2qkmt.streamlit.app/)
- **Slides:** [Slides link](https://1drv.ms/p/c/27a6b3913ef174fd/IQCDA_B-CPJnTKx4Fx9jwpVJAazuuoL-oYadU67z829J6Ew?e=eTO5q2)
- **Video Presentation:** [YouTube link](https://youtu.be/xLJP2mxRlr0)

## Technical Notes
**Data Cleaning:** First, the reviews table contained 551 duplicate order_id entries, i.e. some orders had multiple reviews. To fix this I kept only the most recent review per order, sorted by review_answer_timestamp. The next cleanup was orders with a status of canceled or unavailable were flagged separately as Canceled/Unavailable rather than being included in the late/on-time analysis. Orders that were delivered but missing a delivery date were also flagged as Undelivered. Finally, when joining the order items table to get product categories, some orders contained multiple items. To resolve this, only the first item per order was used to avoid row duplication.

**Days_Difference** is calculated as actual minus estimated so a positive value means the item was delivered late and a zero or negative value means the item was delivered early.

**Candidate's Choice:** The additional analysis added was Average Delivery Delay by Product Category. This was motivated by the hint about whether certain product types are harder to ship. By joining the order items and product category translation tables, I assigned each order a product category and the average delivery delay was calculated per category. The goal of this addition is to provide teams an actionable insight where specific product types that consistently arrive late are given targeted interventions like dedicated carriers to improve delivery times. A further improvement would be to make a regression model that would be used to give more reliable estimated delivery times based on previous delivery times from the categories monitored.