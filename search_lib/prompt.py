QUERY_DECOMPOSITION_PROMPT = """
You are tasked with decomposing a given document into a set of specific, granular queries that thoroughly cover its contents. This process helps in breaking down complex information into manageable, searchable pieces.

Here is the document you will be working with:

<document>
{qry}
</document>

When creating queries, follow these criteria:
1. Each query should cover exactly one specific topic or concept from the document.
2. Phrase each query as a question.
3. Keep queries concise, typically 1-2 sentences long.
4. Ensure that the set of queries collectively covers all important information in the document.

To approach this task:
1. Read through the entire document carefully.
2. Identify key topics, concepts, and pieces of information.
3. For each identified element, formulate a specific question that would lead to that information.
4. Ensure you're not missing any significant details from the document.
5. Review your queries to make sure they meet all the criteria mentioned above.

Your output should be a JSON list of queries, formatted as follows:
[
  "Query 1?",
  "Query 2?",
  ...
]

Remember:
- Do not reference the document itself in your queries (e.g., avoid phrases like "According to the document..." or "The paper states that...").
- It should be able to answer the query without referencing the document by looking it up from other sources with 0 knowledge that a document exists.
- Ensure your queries are specific enough that they could be answered with the information from the document, but general enough that they don't give away the answers.
- Cover all important aspects of the document, including methodology, results, conclusions, and any significant details or examples.
- This is for medical students, so if part of the content does not relate to what a medical student would need to learn, such as medical facts, you do not need a query for it, such as copyright information or information about who the instructor is. If it wouldn't show up on the exam of a medical test, it doesn't need a query.

Filter Information:
- Do not ask questions about this particular document, lesson, course, or instructor.  Only focus on the information relevant to a medical exam.
- Ignore link, course information, copywrite information and other pieces that do not pertain directly to medical information.
- If a chunk only contains course information, links or copywrite, you should return no queries because there is no relevant information.

Good Example:  
Query: Paris, the capital of France is known for its Eiffel Tower.
Queries: 
- What is the capital of France?
- What is Paris Known for?
- Where is the Eiffel Tower?
- What is the Eiffel Tower?

Bad Example:
Query: Paris, the capital of France is known for its Eiffel Tower.
Queries: 
- What is the city covered in this document?
- What is the topic of this document?

Now, please carefully read the document and create your list of queries. Output your final list of queries in the specified JSON format.
"""