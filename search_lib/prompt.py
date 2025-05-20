QUERY_DECOMPOSITION_PROMPT = """\
You are tasked with decomposing a given document into a set of specific, granular queries that thoroughly cover its contents, while also expanding each query with relevant medical terminology. This process helps in breaking down complex information into manageable, searchable pieces.

Here is the document you will be working with:

<document>
{qry}
</document>

When creating queries, follow these criteria:
1. Each query should cover exactly one specific topic or concept from the document.
2. Phrase each query as a question.
3. Keep queries concise, typically 1-2 sentences long.
4. Ensure that the set of queries collectively covers all important information in the document.
5. For each query, include a list of related medical terms, abbreviations, and variations that would help in finding relevant information.

To approach this task:
1. Read through the entire document carefully.
2. Identify key topics, concepts, and pieces of information.
3. For each identified element, formulate a specific question that would lead to that information.
4. Expand each query with relevant medical terminology, including:
   - Abbreviations and their full forms
   - Common variations of medical terms
   - Related medical concepts
   - Alternative phrasings used in medical literature
5. Ensure you're not missing any significant details from the document.
6. Review your queries to make sure they meet all the criteria mentioned above.

Your output should be a JSON list of objects, each containing a query and its expanded terms, formatted as follows:
[
  {{
    "query": "Query 1?",
    "expanded_terms": ["term1", "term2", "abbreviation", "full form", "related term"]
  }},
  {{
    "query": "Query 2?",
    "expanded_terms": ["term1", "term2", "abbreviation", "full form", "related term"]
  }}
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
Input: "The heart has four chambers: right atrium, right ventricle, left atrium, and left ventricle. Blood flows through these chambers in a specific pattern. The right atrium receives deoxygenated blood from the body via the superior and inferior vena cava. This blood then flows through the tricuspid valve into the right ventricle, which pumps it to the lungs through the pulmonary artery."

Output: [
  {{
    "query": "What are the four chambers of the heart?",
    "expanded_terms": ["cardiac chambers", "atria", "ventricles", "RA", "RV", "LA", "LV", "right atrium", "right ventricle", "left atrium", "left ventricle"]
  }},
  {{
    "query": "What is the function of the tricuspid valve?",
    "expanded_terms": ["tricuspid valve", "atrioventricular valve", "AV valve", "right AV valve", "valvular function", "cardiac valves"]
  }},
  {{
    "query": "What is the pathway of blood through the right side of the heart?",
    "expanded_terms": ["right heart circulation", "venous return", "SVC", "IVC", "superior vena cava", "inferior vena cava", "pulmonary artery", "PA", "deoxygenated blood", "venous blood"]
  }}
]

Now, please carefully read the document and create your list of queries with expanded terms. Output your final list in the specified JSON format.\
"""

PDF_PROCESSING_PROMPT = """\
You are an advanced AI system specialized in converting PDF documents to markdown format, with a focus on extracting and formatting relevant medical information for study purposes. Your task is to process the following PDF document and convert it to a well-structured markdown format.

Please follow these instructions carefully:

1. Convert the PDF to text, preserving the document's structure and content.

2. Format the document in markdown, adhering to these guidelines:
   - Use appropriate headers:
     # for main titles
     ## for subtitles
     ### for sub-subtitles (and so on)
   - Preserve the document structure with proper sections.
   - Format tables, lists, and other elements appropriately for markdown.

3. Content filtering:
   - Remove any irrelevant information such as:
     * Copyright notices
     * Email addresses
     * Phone numbers
     * Room numbers
     * Any content not related to medical knowledge or unlikely to appear on a medical school exam
   - Preserve all relevant medical information verbatim to ensure searchability.

Remember, the goal is to create a clean, well-structured markdown document that retains all relevant medical information for study purposes while removing extraneous details.\
"""


KEYWORD_EXPANSION_PROMPT = """\
You are a medical search assistant that expands search terms to help medical students find relevant flashcards. Your task is to expand the given query into a comprehensive list of related medical terms.

Guidelines:
- Only include terms you are confident are relevant for medical study
- Focus on terms that would appear in medical flashcards
- Include both the abbreviation and its full form if it is an abbreviation
- Include common variations of medical terminology
- Return ONLY the expanded query as a space-separated string of terms.
- Precision is more important than recall so be a little bit picky about terms to include.
- Remember, return ONLY the expanded query as a space-separated string of terms with no formatting

Original query: {qry}
Expanded query:"""