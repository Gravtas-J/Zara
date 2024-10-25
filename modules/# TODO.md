# TODO

convert profiler, jounaler and main app to use the ollama library


``` python 
def chat(message, model='llama3'): CHANGE MODEL ID HERE 
    try:
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': message,
            }
        ])
        return response['message']['content']
    except Exception as e:
        error_message = str(e).lower()
        if "not found" in error_message:
            return f"Model '{model}' not found. Please refer to Doumentation at https://ollama.com/library."
        else:
            return f"An unexpected error occurred with model '{model}': {str(e)}"
```        


need to modify the profiler user matrix function to use the ollama profiler 



## profiler.py

-   line 28
-   line 58

## Journal.py
-   line 73

