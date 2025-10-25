import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.REACT_APP_GEMINI_API_KEY);

export const getStateInfo = async (stateName) => {
    try {
        const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-lite" });

        const prompt = `Find recent news articles and government legislation related to AI data centers in ${stateName}. 
        Provide:
        1. 3 recent news articles with titles and brief summaries
    
        Format the response as such:
        TITLE 1
        SUMMARY 1
        TITLE 2
        SUMMARY 2
        TITLE 3
        SUMMARY 3

        Do not include anything in your output other than the three titles and summaries. Do not prefix title or summary with anything.
        The output should only contain the three titles and summaries, no other output. `;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
    
        return {
          success: true,
          data: text
        };
      } catch (error) {
        console.error("Error calling Gemini API:", error);
        return {
          success: false,
          error: error.message
        };
      }
};
