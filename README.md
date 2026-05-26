
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

# Project Brief: The "Last Mile" Logistics Auditor

**Client:** Veridi Logistics (Global E-Commerce Aggregator)  
**Deliverable:** Public Dashboard, Code Notebook & Insight Presentation

---

## 1. Business Context
**Veridi Logistics** manages shipping for thousands of online sellers. Recently, the CEO has noticed a spike in negative customer reviews. She has a "gut feeling" that the problem isn't just that packages are late, but that the estimated delivery dates provided to customers are wildly inaccurate (i.e., we are over-promising and under-delivering).

She needs you to audit the delivery data to find the root cause. She specifically wants to know: **"Are we failing specific regions, or is this a nationwide problem?"**

Your job is to build a "Delivery Performance" audit tool that connects the dots between **Logistics Data** (when a package arrived) and **Customer Sentiment** (how they rated the experience).

## 2. The Data
You will use the **Olist E-Commerce Dataset**, a real commercial dataset from a Brazilian marketplace. This is a relational database dump, meaning the data is split across multiple CSV files.

* **Source:** [Kaggle - Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
* **Key Files to Use:**
    * `olist_orders_dataset.csv` (The central table)
    * `olist_order_reviews_dataset.csv` (Sentiment)
    * `olist_customers_dataset.csv` (Location)
    * `olist_products_dataset.csv` (Categories)

## 3. Tooling Requirements
You have the flexibility to choose your development environment:

* **Option A (Recommended):** Use a cloud-hosted notebook like **Google Colab**, or **Deepnote**, etc.
* **Option B:** Use a local **Jupyter Notebook** or **VS Code**.
    * *Condition:* If you choose this, you must ensure your code is reproducible. Do not reference local file paths (e.g., `C:/Downloads/...`). Assume the dataset is in the same folder as your notebook.
* **Dashboarding:** The final output must be a **publicly accessible link** (e.g., Tableau Public, Google Looker Studio, Streamlit Cloud, or PowerBI Web, etc.).

---

## 4. User Stories & Acceptance Criteria

### Story 1: The Schema Builder
**As a** Data Engineer,  
**I want** to join the Orders, Reviews, and Customers tables into a single master dataset,  
**So that** I can analyze a customer's location and their review score in the same row.

* **Acceptance Criteria:**
    * Load the raw CSVs into your notebook.
    * Perform the correct joins (e.g., join Reviews to Orders on `order_id`, join Customers to Orders on `customer_id`).
    * **Check:** Ensure you don't accidentally duplicate rows (a common error with 1-to-many joins).

### Story 2: The "Real" Delay Calculator
**As a** Logistics Manager,  
**I want** to know the difference between the "Estimated Delivery Date" and the "Actual Delivery Date,"  
**So that** I can see how often we are lying to customers.

* **Acceptance Criteria:**
    * Create a new calculated column: `Days_Difference` = `order_estimated_delivery_date` - `order_delivered_customer_date`.
    * Classify orders into statuses: "On Time", "Late", and "Super Late" (> 5 days late).
    * Handle missing values: Some orders were never delivered (`order_status` = 'canceled' or 'unavailable'). These should be excluded or flagged separately.

### Story 3: The Geographic Heatmap
**As a** Regional Director,  
**I want** to see which specific States (`customer_state`) have the highest percentage of late deliveries,  
**So that** I can focus my repair efforts on the worst regions.

* **Acceptance Criteria:**
    * Calculate the % of late orders per State.
    * Visualize this on a map or a bar chart.
    * **Insight:** Identify if "Remote" states (far from the distribution center) are disproportionately affected.

### Story 4: The Sentiment Correlation
**As a** Customer Success Lead,  
**I want** to see if late deliveries actually cause bad reviews,  
**So that** I can prove to the CEO that logistics is the problem.

* **Acceptance Criteria:**
    * Create a visualization comparing "Delivery Delay (Days)" vs "Average Review Score (1-5)".
    * Show the average review score for "On Time" orders vs. "Late" orders.

---

## 5. Bonus User Story: The "Translation" Challenge
**As a** Global Analyst,  
**I want** to see product categories in **English**, not Portuguese,  
**So that** I can understand if "Furniture" is harder to ship than "Electronics".

* **Acceptance Criteria:**
    * The `product_category_name` is in Portuguese (e.g., `cama_mesa_banho`).
    * Use the `product_category_name_translation.csv` file included in the dataset (or create your own mapping) to translate these into English for your final dashboard.

---

## 6. The "Candidate's Choice" Challenge
**As a** Creative Problem Solver,  
**I want** to include one extra feature or analysis that adds specific business value,  
**So that** I can demonstrate my ability to think beyond the basic requirements.

* **Instructions:**
    * Add one more metric, chart, or drill-down.
    * **Requirement:** You must justify *why* this feature matters to the business in your README.

---

## 7. Submission Guidelines
Please edit this `README.md` file in your forked repository to include the following three sections at the top:

### A. The Executive Summary
* A 3-5 sentence summary of your findings.

### B. Project Links
* **Link to Notebook:** (e.g., Google Colab, etc.). *Ensure sharing permissions are set to "Anyone with the link can view".*
* **Link to Dashboard:** (e.g., Tableau Public, etc.).
* **Link to Presentation:** A link to a short slide deck (PDF/PPT) AND (Optional) a 2-minute video walkthrough (YouTube) explaining your results.

### C. Technical Explanation
* Briefly explain how you handled the "Data Cleaning".
* Explain your "Candidate's Choice" addition.

**Important Note on Code Submission:**
* Upload your `.ipynb` notebook file to the repo.
* **Crucial:** Also upload an **HTML or PDF export** of your notebook so we can see your charts even if GitHub fails to render the notebook code.
* Once you are ready, please fill out the [Official Submission Form Here](https://forms.office.com/e/heitZ9PP7y) with your links

---

## 🛑 CRITICAL: Pre-Submission Checklist

**Before you submit your form, you MUST complete this checklist.**

> ⚠️ **WARNING:** If you miss any of these items, your submission will be flagged as "Incomplete" and you will **NOT** be invited to an interview. 
>
> **We do not accept "permission error" excuses. Test your links in Incognito Mode.**

### 1. Repository & Code Checks
- [x] **My GitHub Repo is Public.** (Open the link in a Private/Incognito window to verify).
- [x] **I have uploaded the `.ipynb` notebook file.**
- [x] **I have ALSO uploaded an HTML or PDF export** of the notebook.
- [x] **I have NOT uploaded the massive raw dataset.** (Use `.gitignore` or just don't commit the CSV).
- [x] **My code uses Relative Paths.** 

### 2. Deliverable Checks
- [x] **My Dashboard link is publicly accessible.** (No login required).
- [x] **My Presentation link is publicly accessible.** (Permissions set to "Anyone with the link can view").
- [x] **I have updated this `README.md` file** with my Executive Summary and technical notes.

### 3. Completeness
- [x] I have completed **User Stories 1-4**.
- [x] I have completed the **"Candidate's Choice"** challenge and explained it in the README.

**✅ Only when you have checked every box above, proceed to the submission form.**

---
