from google import genai
import config
def AIdata(experience, about):
   
    client = genai.Client(api_key=config.API)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f" {experience} {about}------- from the given data tell me the area of expertise and what programming language he uses the most if not able to determine then return most relevent programming language according to the data and reply in 2-3 words only ",
        )
    return response.text


