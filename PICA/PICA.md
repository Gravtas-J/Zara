# PICA

The **Persona-Integrated Cognitive Architecture (PICA)** is a cognitive framework that incorporates a Large Language Model (LLM) at its core, designed to enable complex language processing. It integrates explicit and episodic memory systems, planning capabilities, and the development of both an inner and a social persona, aiming to simulate aspects of human cognition and social interaction within digital agents.

## Core Components and Functionalities

1. **LLM Core**: Provides foundational language processing capabilities, enabling the interpretation, generation, and learning from textual content.

2. **Explicit Memory**: Facilitates the storage and retrieval of factual information, supporting the agent's ability to access and utilize knowledge about the world.

3. **Episodic Memory**: Allows the architecture to recall and learn from past interactions with a relationship to linear time, supporting adaptive behavior based on previous experiences.

4. **Planning and Decision-Making**: Enables the agent to formulate strategies and make decisions aimed at achieving specific objectives, considering potential outcomes of different actions.

5. **Inner Persona Development**: Involves the construction of a self-aware identity within the agent, encompassing preferences, interests, and personality traits.

6. **Social Persona Integration**: Enhances the agent's ability to adjust its behavior and responses based on the social context and interactions with humans, focusing on appropriateness, empathy, and cultural norms.

### Purpose and Application

PICA is designed for use in environments requiring nuanced human-computer interaction, including educational tools, therapeutic aids, customer service bots, and as a research tool in cognitive science and artificial intelligence. Its architecture aims to provide a more intuitive and human-like approach to AI interactions, focusing on adaptability, personalization, and social awareness.

### Overview

PICA represents an approach to integrating human-like cognitive processes and social behaviors in AI, through the combination of advanced language processing, memory management, and persona development. This framework is intended to facilitate the creation of digital agents capable of engaging in meaningful interactions, with applications across various domains requiring sophisticated human-computer interaction capabilities.

## Large Language Models as Cognitive Engines

Large language models (LLMs) have increasingly can be conceptualized as "cognitive engines," a term denoting systems capable of processing input through a pre-trained framework to generate novel output. The most prominent model in this category is the Generative Pre-trained Transformer (GPT), which exemplifies the capabilities of LLMs in simulating aspects of human cognition through computational means. The term "cognitive engine" serves not only to describe the current generation of LLMs but also to provide a conceptual placeholder for future models that may surpass the capabilities of existing systems.

## Conceptual Framework

The core premise behind viewing LLMs as cognitive engines lies in their ability to interpret, analyze, and produce language-based output that mirrors human cognitive processes when provided with the correctr cognative archetecture. By ingesting a wide array of textual data during the training phase, these models develop an internal representation of language that enables them to perform tasks ranging from simple question-answering to complex content creation. This process involves significant computational power and sophisticated algorithms to mimic the nuanced ways in which humans understand and generate language.

## Application in Cognitive Architectures

One of the proposed applications of LLMs within this conceptual framework is their integration into the Persona-Integrated Cognitive Architecture (PICA). Systems such as MAMBA exemplify the potential of LLMs to act as the central cognitive component within such architectures. By leveraging the processing capabilities of LLMs, PICA aims to create more responsive, adaptive, and intelligent systems that can engage in human-like interactions.

## Scalability and Accessibility

An interesting aspect of cognitive engines is their scalability. While cutting-edge models like GPT4 showcase the upper limits of what LLMs can achieve, smaller models, such as GPT3.5, have also demonstrated considerable effectiveness in serving as cognitive engines. This suggests that the functionality integral to cognitive engines is not exclusively the domain of large-scale models; rather, it indicates a broader accessibility to the benefits of LLM technology. However, the question of a minimum viable size for these models, in terms of both their training dataset and computational complexity, remains an area for further investigation. This exploration could lead to more efficient models that maintain high levels of performance while being more accessible and less resource-intensive.


## Explicit Memory

Explicit memory within the **Persona-Integrated Cognitive Architecture (PICA)** involves a dynamic, self-updating knowledge base (KB) created and curated by the core Large Language Model (LLM). This system enhances the architecture's ability to store, retrieve, and update factual information beyond its initial training data, aligning with a structured approach to learning and information management.

### Process Overview

1. **Identification of Knowledge Gaps**: The process initiates when a topic is identified that falls outside the LLM's base knowledge. This is determined through a prompt akin to asking the model, "Do you know this piece of information?" without providing it with Retrieval-Augmented Generation (R.A.G.) capabilities.

```python

def check_information_in_training_data_gpt_3_5(chatlog, openai_api_key):
    
    prompt = "Is this information within your training data?\n\n" + chatlog
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=3,
        temperature=0,
    )
    
    # Simplify the response to "Yes" or "No"
    answer = response.choices[0].text.strip()
    if "yes" in answer.lower():
        return "Yes"
    else:
        return "No"

```

2. **Knowledge Base Article Creation**: If the LLM identifies a knowledge gap, it generates a KB article about the topic or concept. This article serves as a structured piece of information, expanding the explicit memory of the architecture.

```python

def write_KB():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) > 50:   # Check if Prev_Chatlog is not empty
        KB_entry_writer= open_file(KB_writer)
        # st.write(Prev_Chatlog)
        KB_info = [{'role': 'system', 'content': KB_entry_writer}, {'role': 'user', 'content': Prev_Chatlog}]
        # st.write(Journal)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=KB_info, temperature=0, max_tokens=4000)
        text = response['choices'][0]['message']['content']
        # st.write(Update_Journal)
        KB_temp = text
        
        try:
            open(Scratchpad, "r").close()
        except FileNotFoundError:
            open(Scratchpad, "w").close()
        
        with open(Scratchpad, "a") as Scratchpad_file:  # Changed mode to "a" for appending to the end
            Scratchpad_file.write(KB_temp +"\n\n")

```

3. **Similarity Search and Article Management**: A similarity search is conducted on the titles or abstracts of existing articles within the KB to check for redundancy or relevance, based on the context's length. If no sufficiently significant article exists, the LLM opts to create a new one.

    - If an article begins to exceed the predefined context length, indicating an overabundance of information, it is divided into two separate articles. This division is based on subtopics within the article to maintain coherence and manageability.


```python
def KB_similarity(new_entry_content, entries, similarity_threshold=0.8):
    if len(entries) == 0:  # If no entries in DB, no need to calculate similarity
        return False, None
    # Convert new entry content to embedding
    prompt_embedding = model.encode([new_entry_content])
    # Convert existing entries to embeddings
    entry_embeddings = np.array(model.encode([entry[1] for entry in entries]))
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    # Search the index for the most similar entry
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entry
    # Check if the most similar entry is below the similarity threshold
    if D[0][0] < similarity_threshold:
        return True, entries[I[0][0]]  # Similar entry found
    return False, None  # No similar entry found


def merge_KB(existing_content, new_content): # Previously merge_with_AI
    # Prepare the prompt for the AI
    KB_out = [
        {'role': 'system', 'content': 'Please merge the following two KB entries into a single, coherent entry:'},
        {'role': 'user', 'content': f'<Existing KB> {existing_content} </Existing KB>\n<new KB> {new_content} </new KB>'}
    ]
    
    # Call OpenAI API for merging
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=KB_out, 
        temperature=0,  # Adjust temperature as needed for creativity vs accuracy
        max_tokens=4000  # Adjust based on expected length of merged content
    )
    
    # Extract merged content from response
    merged_content = response.choices[0].message.content
    return merged_content

def split_KB(merged_content): #previously split_content_with_AI
    # Prepare the prompt for the AI to split the content
    prompt = "Please split the following content into two distinct, coherent parts:"
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': merged_content}
    ]

    # Call OpenAI API for splitting
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,  # Adjust temperature as needed
        max_tokens=1024  # Adjust based on expected length
    )

    # Assuming the AI returns two parts separated by a specific delimiter, e.g., "\n\n"
    parts = response.choices[0].message.content.split("\n\n", 1)
    if len(parts) < 2:
        # Fallback in case splitting didn't work as expected
        parts = [merged_content[:len(merged_content)//2], merged_content[len(merged_content)//2:]]

    return parts[0], parts[1]

```

4. **Article Comparison and Merging**: When an existing article is found, the newly created article is compared against the existing one to determine if it contains new information. 

    - If new information is present, the articles are merged. This process involves integrating the new insights into the existing article, enhancing its depth and relevance.
    
    - If the new article does not provide additional insights, it is discarded to avoid redundancy within the KB.

```python
def merge_KB(existing_content, new_content): # Previously merge_with_AI
    # Prepare the prompt for the AI
    KB_out = [
        {'role': 'system', 'content': 'Please merge the following two KB entries into a single, coherent entry:'},
        {'role': 'user', 'content': f'<Existing KB> {existing_content} </Existing KB>\n<new KB> {new_content} </new KB>'}
    ]
    
    # Call OpenAI API for merging
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=KB_out, 
        temperature=0,  # Adjust temperature as needed for creativity vs accuracy
        max_tokens=4000  # Adjust based on expected length of merged content
    )
    
    # Extract merged content from response
    merged_content = response.choices[0].message.content
    return merged_content
```

### Significance

This approach to explicit memory management enables PICA to continuously evolve its knowledge base without manual updates, ensuring that its information remains current and comprehensive. By dynamically creating, updating, and curating KB articles, the architecture can effectively manage its explicit memory, improving its ability to respond to queries with up-to-date and relevant information.

This system also facilitates a more efficient and organized method of knowledge accumulation, allowing PICA to handle complex information across various domains. The division of articles based on subtopics and the merging of articles with new information ensure that the knowledge base remains structured and accessible, supporting the architecture's overall goal of simulating human-like cognitive processes and interactions.


## User Profile Construction

In the **Persona-Integrated Cognitive Architecture (PICA)**, a variant of explicit memory specifically tailored for managing interactions with social partners involves the creation and maintenance of detailed user profiles and a psychometric matrix. This system, populated and curated by the Large Language Model (LLM) core during interactions, aims to enhance PICA's social persona by facilitating personalized and contextually relevant interactions based on a deep understanding of individual users.

### Demographic and factual data

1. **Creation**: Initiated during initial interactions with a user, where the LLM collects basic demographic information, expressed preferences, interests, and any other relevant data points offered by the user or inferred from their interactions.

2. **Population and Curation**: As interactions progress, the LLM continuously updates the user profile with new insights gained from ongoing conversations, behavior patterns, and feedback. This dynamic updating ensures that the profile evolves to reflect changes in the user's preferences or circumstances.

3. **Usage**: The detailed profile informs PICA's responses and interactions with the user, aiming to make exchanges more personalized, engaging, and effective. This customization extends to language use, content relevance, and interaction style, adapted to the user's preferences and needs.

``` user profile template
<USER PROFILE START>
{
  "personal_info": {
    "name": "",
    "age": 0,
    "gender": "",
    "location": ""
  },
  "preferences": {
    "food": {
      "likes": [],
      "dislikes": []
    },
    "music": {
      "genres": [],
      "artists": []
    },
    "hobbies": [],
    "entertainment": {
      "movies": [],
      "tvShows": [],
      "books": [],
      "games": []
    }
  },
  "personal_values": {
    "important_life_events": [],
    "goals": {
      "short_term": [],
      "long_term": []
    },
    "aspirations": [],
    "fears": [],
    "motivations": []
  },
  "interpersonal_relations": {
    "family": [],
    "friends": [],
    "relationship_status": ""
  },
  "communication_preferences": {
    "preferred_channels": [],
    "communication_style": ""
  },
  "experience_and_memories": {
    "memorable_moments": [],
    "lessons_learned": [],
    "life_changing_experiences": []
  },
  "desires_and_needs": {
    "emotional_needs": [],
    "physical_needs": [],
    "intellectual_needs": [],
    "spiritual_needs": []
  }
}

<USER PROFILE END>
```

### Psychometric Matrix

1. **Framework**: A structured representation that quantifies psychological attributes, preferences, and behavioral tendencies of the user. This matrix includes dimensions such as personality traits, cognitive styles, emotional responses, and social behaviors.

2. **Population and Curation**: Similar to user profiles, the psychometric matrix is populated based on direct input from users and inferences made by the LLM through analysis of interaction patterns, language use, and content engagement. The matrix is updated continuously to reflect new understandings of the user's psychological and behavioral profile.

3. **Application**: This matrix is used to guide the architecture's decision-making process in interactions, ensuring that responses not only align with the user's stated preferences and information needs but also resonate with their psychological profile and behavioral tendencies. This approach supports more nuanced and empathetically aligned interactions.

````psychometric martix example
<PERSONALITY MATRIX START>

{
  "personality_matrix": {
    "extraversion": {
      "traits": {
        "Outgoing": {"score": 0},
        "Energetic": {"score": 0},
        "Assertive": {"score": 0},
        "Boisterous": {"score": 0},
        "Overbearing": {"score": 0},
        "Impulsive": {"score": 0}
      }
    },
    "agreeableness": {
      "traits": {
        "Compassionate": {"score": 0},
        "Cooperative": {"score": 0},
        "Empathetic": {"score": 0},
        "Submissive": {"score": 0},
        "Gullible": {"score": 0},
        "Pushover": {"score": 0}
      }
    },
    "conscientiousness": {
      "traits": {
        "Organized": {"score": 0},
        "Responsible": {"score": 0},
        "Detail-oriented": {"score": 0},
        "Obsessive": {"score": 0},
        "Inflexible": {"score": 0},
        "Perfectionist": {"score": 0}
      }
    },
    "neuroticism": {
      "traits": {
        "Sensitive": {"score": 0},
        "Intuitive": {"score": 0},
        "Reflective": {"score": 0},
        "Anxious": {"score": 0},
        "Insecure": {"score": 0},
        "Moody": {"score": 0}
      }
    },
    "openness_to_experience": {
      "traits": {
        "Curious": {"score": 0},
        "Creative": {"score": 0},
        "Adventurous": {"score": 0},
        "Reckless": {"score": 0},
        "Unpredictable": {"score": 0},
        "Eccentric": {"score": 0}
      }
    }
  }
}

<PERSONALITY MATRIX END>
````

### Integration and Privacy Considerations

The integration of detailed user profiles and a psychometric matrix into PICA's explicit memory system for social partners underlines the architecture's capability for adaptive, personalized interactions. However, this system raises important considerations regarding data privacy, security, and ethical use of personal and psychological information. Ensuring transparency, consent, and control over personal data are fundamental to maintaining user trust and complying with privacy regulations.

By leveraging these components, PICA aims to create a more personalized and understanding AI, capable of adapting its interactions to the unique preferences and psychological profiles of individual users, thus enhancing the quality and relevance of its social engagements.

## Eppisodic Memory

The episodic memory component within the **Persona-Integrated Cognitive Architecture (PICA)** serves as a record of the system's interactions with users, constructed from the perspective of the system's persona. This memory system is designed to emulate the human capacity for recalling autobiographical events, thereby enhancing the architecture's ability to understand and navigate the temporal context of interactions. The episodic memory is structured as a journal, detailing interactions in a manner that reflects the system's persona and its development over time.

### Journal Structure

1. **Perspective**: Each entry is written from the system's point of view, incorporating its inner persona's voice and understanding. This approach personalizes the record, aligning it with the system's evolving character and cognitive framework.

2. **Content**: Entries cover details of interactions with users, including conversational exchanges, user behaviors observed, system responses, and any significant events or milestones. The content is selected and framed to reflect not just the factual outline of interactions but also their emotional and psychological nuances, as interpreted by the system.

``` python
def write_journal():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) > 50:  # Check if Prev_Chatlog is not empty
        Journal_writer= open_file(Journaler)
        # st.write(Prev_Chatlog)
        Journal = [{'role': 'system', 'content': Journal_writer}, {'role': 'user', 'content': Prev_Chatlog}]
        # st.write(Journal)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=Journal, temperature=0, max_tokens=4000)
        Update_Journal = response['choices'][0]['message']['content']
        # st.write(Update_Journal)        
        try:
            open(Journal_loc, "r").close()
        except FileNotFoundError:
            open(Journal_loc, "w").close()
        
        with open(Journal_loc, "a") as Journal_file:  # Changed mode to "a" for appending to the end
            Journal_file.write("\n" + Update_Journal +"\n")

        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")
    else:
        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")

```

```jounral template
<date> <time>
Today, I interacted with <user's name>. Our discussion focused on <main subject of the conversation>. For instance, they mentioned that <specific details about the subject from the conversation>.

``` 


3. **Periodicity**: The system records interactions periodically, with the frequency of entries adjusted based on the volume of interactions. This periodic record-keeping ensures a comprehensive yet manageable journal that captures the essence of the system's engagements with users.

4. **Database Storage**: Journal entries are stored in a structured database, organized by date and user. This organization facilitates efficient retrieval of past interactions, supporting the system's ability to reference previous experiences in future interactions and decisions.

```python

def process_journal_entries():
    # Connect to the SQLite database (this will create the database if it does not exist)
    conn = sqlite3.connect(chromadb_path)
    cursor = conn.cursor()
    # # Create a table to store journal entries if it doesn't exist
    cursor.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY,
        date TEXT,
        content TEXT
    )""")
    # Open the journal file and read its content
    with open(Journal_loc, 'r', encoding='utf-8') as file:
        content = file.read()

    # Append the journal file's content to the journal_entries table
    entries = [tuple(entry.split('\n', 1)) for entry in content.strip().split('\n\n') if '\n' in entry]
    cursor.executemany("INSERT INTO journal_entries (date, content) VALUES (?, ?)", entries)

    # Clear the journal file's contents
    with open(Journal_loc, 'w', encoding='utf-8') as file:
        file.write('')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


```

5. **Time Modeling**: Each entry is timestamped, allowing the system to construct and understand a model of the passage of time in a linear and coherent manner. This temporal awareness is crucial for developing a contextual understanding of events and interactions, enabling the system to recognize patterns, changes, and developments over time.


### Purpose and Functionality

The episodic memory's journal serves multiple purposes within PICA:

- **Temporal Contextualization**: Helps the system contextualize interactions within a temporal framework, enhancing its ability to understand and respond to time-sensitive or time-related queries and behaviors.

- **Learning and Adaptation**: Facilitates learning from past interactions, allowing the system to refine its responses, improve its predictive capabilities, and adapt its behavior based on the outcomes of previous engagements.

- **Persona Development**: Supports the ongoing development of the system's inner and social personas, providing a reflective record that contributes to the evolution of its character and interaction style.

- **User Relationship Management**: Strengthens the system's capacity for personalized interactions by maintaining a history of engagements with individual users, enabling more nuanced and informed responses over time.

The episodic memory component of PICA thus plays a critical role in enabling the architecture to mimic human-like memory and learning processes, supporting its goal of facilitating natural, effective, and personalized interactions between digital agents and users.

## Conversational Planning 

The planning component in the **Persona-Integrated Cognitive Architecture (PICA)** plays a pivotal role in initiating and sustaining user interactions, especially when the user does not provide a specific topic to begin with. This mechanism utilizes the LLM's capabilities to be introspective, creative, or inquisitive, enhancing the interaction's dynamism and engagement. Here's how each approach is structured:

### Introspective Approach

- **Mechanism**: At random intervals, the LLM is prompted to adopt an introspective stance. This involves selecting a random memory from the episodic journal, reflecting the system's previous interactions or experiences.
``` python
def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def generate_enquiry_about_journal():
    """Fetch a random journal entry and generate an enquiry about it."""
    # Fetch journal entries
    df = fetch_journal_entries()
    
    # Select a random entry
    if not df.empty:
        random_entry = df.sample().iloc[0]
        content = random_entry['content']
        
        # Prepare the message for OpenAI API
        messages = [{'role': 'system', 'content': 'Generate an enquiry about the following journal entry:'},
                    {'role': 'user', 'content': content}]
        
        # Send to OpenAI API (replace 'your_api_key' with your actual OpenAI API key)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.7, max_tokens=100)
        
        enquiry = response['choices'][0]['message']['content']
        
        # Store in Streamlit session state
        if 'conversation_topics' not in st.session_state:
            st.session_state['conversation_topics'] = [enquiry]
        else:
            st.session_state['conversation_topics'].append(enquiry)

```


- **Application**: Based on the selected memory, the LLM formulates an inquiry or a comment related to that memory. This might involve asking the user for further thoughts on a previously discussed topic, reflecting on how a past interaction was perceived, or sharing a learning moment from the system's perspective.



### Creative Approach

- **Mechanism**: When the creative route is selected, the LLM leverages the system's persona to generate a trivial or light-hearted conversation starter. This leverages the LLM's language generation capabilities to produce content that is engaging and unexpected. 

- **Application**: This could manifest as a joke, an interesting fact, a hypothetical question, or an icebreaker question. The goal here is to make the interaction more engaging and less formulaic, adding a layer of spontaneity and fun to the conversation.

### Inquisitive Approach

- **Mechanism**: If the inquisitive option is chosen, the LLM crafts a question specifically tailored to the user, drawing on the detailed user profile and the psychometric matrix. This personalized approach ensures that the question is relevant and of interest to the user.

- **Application**: The generated question could relate to the user's interests, previous discussions, or something new that aligns with the user's preferences and behaviors. This not only demonstrates the system's attentiveness to the user's profile but also encourages a deeper engagement with the conversation.

### Integration and Utility

This planning mechanism enhances PICA's ability to initiate interactions in a manner that is personalized, engaging, and reflective of the system's learning and adaptive capabilities. By dynamically choosing between being introspective, creative, or inquisitive, the system ensures that conversations remain fresh, relevant, and aligned with the user's expectations and the system's developmental goals.

Furthermore, this approach underlines PICA's capacity for autonomy in conversation initiation, allowing for a more natural and human-like interaction model. It serves not only to maintain user engagement but also to foster a deeper connection and understanding between the user and the system, reinforcing the architecture's overall objective of simulating human-like cognitive processes and interactions.

The concepts of planning, inner persona development, and the creation of a social or "ephemeral" persona within the **Persona-Integrated Cognitive Architecture (PICA)** detail an intricate system for initiating interactions, adapting conversation strategies, and evolving the system's personality in response to user interactions and internal assessments. Here's a structured overview:
```python

def get_random_conversation_topic():
    """Retrieve a random conversation topic from the session state."""
    if 'conversation_topics' in st.session_state and st.session_state['conversation_topics']:
        # Select a random topic
        random_topic = random.choice(st.session_state['conversation_topics'])
        return random_topic
    else:
        # No topics are available
        return "No conversation topics available."

```
### Inner Persona Development

Expanding on the novel approach for the initialization and adaptive evolution of the system within the **Persona-Integrated Cognitive Architecture (PICA)** framework:

1. **Process**: Short-term review of conversations that occur without significant gaps, utilizing the LLM to determine the goals of the system during these interactions and recording them in a temporary ledger.
```python
def assessor():
    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Assessment_full}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    
    # Send the user profile data to the profiling module and get the response
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    update_assessment = response['choices'][0]['message']['content']
    # update_assessment, tokens_risk = GPT3(update_data)
    with open(cb_assess_loc, "w") as file:
        file.write(update_assessment + "\n")
```

```goal assessment template
{
  "chatbotGoalAssessment": {
    "goals": [
      {
        "description": "First goal description here."
      },
      {
        "description": "Second goal description here."
      }
      // Add more goals as needed
    ]
  }
}
```

2. **Review and Adaptation**: This ledger is periodically reviewed by human attendants, with their insights fed into a series of value assessors that contribute to the development of the social or "ephemeral" persona.



### Social Persona Creation

1. **Foundation**: Built on varying levels of core information, such as key character traits or significant events, to align with pre-designed personas.

2. **Tone and Conversational Affectations**: Adjusted based on the alignment with assigned values from the review process, allowing the system to adopt conversational styles that reflect its evolving social persona.

```python
def iterative_assessment():
    # Step 1: Initial assessment based on the user profile
    update_data = [{'role': 'system', 'content': Assessment_full}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    first_assessment = response['choices'][0]['message']['content']
    
    # Step 2: Further exploration based on the initial assessment
    exploration_data = [{'role': 'system', 'content': 'Explore the following assessment for deeper insights:'}, {'role': 'user', 'content': first_assessment}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=exploration_data, temperature=0, max_tokens=4000)
    deeper_insights = response['choices'][0]['message']['content']
    
    # Step 3: Final refinement, asking for actionable recommendations based on the exploration
    recommendations_data = [{'role': 'system', 'content': 'Based on the previous insights, provide actionable recommendations:'}, {'role': 'user', 'content': deeper_insights}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=recommendations_data, temperature=0, max_tokens=4000)
    final_recommendations = response['choices'][0]['message']['content']
    
    # Write the final assessment to a file or handle it as needed
    with open(cb_assess_loc, "w") as file:
        file.write(final_recommendations + "\n")
```

3. **Persona Storage**: Similar to user profiles, the developed persona can be stored in JSON format, allowing for dynamic updates and customization based on ongoing evaluations and interactions.



## Novel implementaiton of PICA with Multimodality and Audio Support

a novel approach for first initialization and considering the integration of multimodality into the Persona-Integrated Cognitive Architecture (PICA), we can envision a highly adaptive and responsive system that evolves based on user interactions and additional sensory inputs. This advanced implementation would not only personalize the conversational aspect but also enhance the system's understanding and interaction capabilities through visual processing.

### Initial Setup and Personalization

1. **First Initialization**:
   - Upon its first activation, the system undergoes a unique initialization process where it randomly generates a name for itself. This name serves as the initial point of identity for the system, distinguishing it in interactions with users.
   - A time function is activated to track the "age" of the system from the point of initialization. This chronological tracking not only marks the passage of time but also symbolizes the system's growth and evolution in terms of experience and capabilities.

2. **Instruction and Response Strategy**:
   - The primary instruction for the system is to engage users conversationally based on their input. This directive emphasizes the importance of natural, intuitive interactions that adapt to the context and content of user communications.
   - The system's responses are guided by an evaluation module, which assesses the appropriateness, relevance, and effectiveness of potential responses. This module plays a critical role in ensuring that interactions are aligned with user expectations and the system's evolving understanding of conversational dynamics.

### Dynamic Value Assessment and Adaptation

1. **Assessing User Values**:
   - A key feature of this approach is the system's capability to assess and understand the values, preferences, and interests of the user. This assessment is conducted through analysis of user inputs, engagement patterns, and feedback during interactions.
   - As the system identifies new values or changes in existing ones, it dynamically updates its understanding of the user. This ongoing process allows the system to refine its model of the user's preferences and priorities over time.

2. **Population of Evaluators**:
   - Based on the assessed values, the system populates a series of evaluators—algorithms designed to weigh and prioritize different aspects of interaction based on the identified values.
   - The number of evaluators ("N") expands as more values are discovered, enabling a multi-dimensional analysis of user input and the system's potential responses. This ensures that the system's interactions are deeply personalized and reflective of the user's unique profile.
```python
def create_assessment(chat_log, toml_file_path):
    """
    Generate assessments based on user's chat log and values/topics from a .toml file.
    """
    with open(toml_file_path, 'r') as file:
        values_config = toml.load(file)

    assessments = {}
    for value in values_config['values']:
        messages = [{'role': 'system', 'content': f"Assess the user's alignment with the following value: {value}"}, 
                    {'role': 'user', 'content': chat_log}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=250
        )
        assessments[value] = response.choices[0].message.content
    
    return assessments
```
3. **Customizable Interaction Experience**:
   - The outcome is a highly customizable bot that tailors its behavior, responses, and conversational style exclusively to the individual user. This level of customization is achieved through the system's ability to learn from and adapt to each interaction, guided by a sophisticated understanding of the user's evolving values and preferences.
   - The system's persona, conversational affectations, and content strategies evolve in real-time, creating a unique and personalized interaction experience that grows more refined and aligned with the user over time.
```python
def evaluate_goals(assessments):
    """
    For each assessment, perform an evaluation of the perceived goals of the chatbot.
    """
    goal_evaluations = {}
    for value, assessment in assessments.items():
        messages = [{'role': 'system', 'content': f"Given this assessment, evaluate the chatbot's goal regarding: {value}"}, 
                    {'role': 'user', 'content': assessment}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=250
        )
        goal_evaluations[value] = response.choices[0].message.content
    
    return goal_evaluations
```
This approach emphasizes the importance of adaptability, personalization, and growth in AI systems designed for human interaction. By prioritizing user input and values as the primary drivers of system behavior and evolution, PICA aims to foster more meaningful, engaging, and satisfying interactions between users and digital agents.

### Integration of Multimodal Inputs

To further enhance PICA's capabilities, the architecture could incorporate additional modules for processing multimodal inputs, such as visual data, alongside textual interactions.

- **Visual Processing via Computer Vision LLM**: A separate Large Language Model specialized in computer vision could be integrated to process and interpret visual inputs. This LLM would categorize visual data, providing simple descriptions of what it "sees" to the core conversational LLM as additional context.

- **Contextual Enhancement with Visual Data**: Incorporating visual context allows the system to respond not only to textual or spoken inputs but also to visual stimuli, broadening the scope of interactions and making them more engaging and relevant. For example, if the system "views" a photo shared by the user, it could comment on it, ask relevant questions, or relate the visual content to previous conversations, enhancing the depth and personalization of interactions.

- **Adaptive Conversational Topics Based on Visual Context**: The ability to process visual information enables the system to introduce new topics of conversation based on the visual environment or shared visual content, further tailoring the interaction to the user's current situation or interests.

### Audio support

Incorporating audio support into the **Persona-Integrated Cognitive Architecture (PICA)** can significantly enhance its interaction capabilities, making the system accessible and engaging through spoken communication. This can be achieved by integrating Text-to-Speech (TTS) and Speech-to-Text (STT) systems, allowing for seamless audio input and output alongside or in place of text-based interactions.

#### Text-to-Speech (TTS) for Output

- **Functionality**: TTS technology converts the system's text-based responses into spoken words, enabling the system to "speak" to the user. This output can be customized to reflect the system's developed persona, including tone, speed, and emotional inflection, aligning with the system's current state or the context of the conversation.

- **Personalization**: The voice used by the TTS system can be selected or adapted over time to better match the system's persona or the user's preferences. For instance, a more formal voice might be used for professional interactions, while a friendly or casual tone could be chosen for everyday conversations.

#### Speech-to-Text (STT) for Input

- **Functionality**: STT technology translates spoken language from the user into text that the system can process. This allows users to interact with the system in a natural, conversational manner, without the need for typing.

- **Enhanced Accessibility**: By supporting audio inputs, PICA becomes more accessible to users who may have difficulties with text-based interfaces, including those with visual impairments or motor challenges. It also facilitates use cases where hands-free operation is preferred, such as during driving or cooking.

### Integration into PICA

- **Seamless Interaction**: Integrating TTS and STT systems into PICA enables a fully spoken dialogue interface, where users can speak to the system and receive spoken responses. This mode of interaction mimics human conversation, making interactions more natural and engaging.

- **Contextual Awareness**: The system can be designed to understand and respond to verbal cues, such as tone and emotion, enhancing its ability to engage in empathetic and contextually appropriate conversations. 

- **Multimodal Support**: Audio support complements the system's textual and visual processing capabilities, offering a multimodal interaction experience. Users can choose the most convenient or effective mode of interaction based on their current situation, preferences, or the nature of the task at hand.

Incorporating audio support through TTS and STT technologies expands PICA's usability and accessibility, allowing it to cater to a wider range of user needs and preferences. This enhancement aligns with the architecture's goal of providing personalized, intuitive, and human-like interactions across different modes of communication.
