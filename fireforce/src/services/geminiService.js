import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.REACT_APP_GEMINI_API_KEY);

export const getStateInfo = async (stateName) => {
    try {
        const model = genAI.getGenerativeModel({ model: "gemini-pro" });

        const prompt = `Find recent news articles and government legislation related to AI data centers in ${stateName}. 
        Provide:
        1. 3-5 recent news articles with titles and brief summaries
        2. Any pending or recent legislation related to AI data centers, power usage, or water usage
        3. Sources/links if available
    
        Format the response in a structured way.`;

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
