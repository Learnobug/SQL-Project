import streamlit as st
import google.generativeai as palm
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("API_KEY")
palm.configure(api_key=GOOGLE_API_KEY)

model = palm.GenerativeModel('models/gemini-pro')


def func():
    st.set_page_config(page_title="SQL Query Generator", page_icon=":robot:")
    st.markdown(
        """ 
        <div style="text-align: center;">
            <h1>SQL Query Generator</h1>
            <h3>I can generate SQL queries for you!</h3>
            <p>This tool is a simple Tool that allows you to generate SQL queries based on your prompts.</p>
        """,
        unsafe_allow_html=True,
    )
   
    database_username=st.text_input("Enter your database username")
    database_password=st.text_input("Enter database password")
    database_host=st.text_input("Enter your database host")
    database_name=st.text_input("Enter your database name")
    text_input = st.text_input("Enter your Query here in plain English:")
    try:
        mydb = mysql.connector.connect(
            host=database_host,
            user=database_username,
            password=database_password,
            database=database_name
        )
        cursor = mydb.cursor()

        # Grant privileges
        grant_query = f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{database_username}'@'%' IDENTIFIED BY '{database_password}';"
        cursor.execute(grant_query)
        mydb.commit()
        print("Privileges granted successfully.")

    except mysql.connector.Error as e:
        print("Error granting privileges:", e)

    submit = st.button("Generate SQL Query")
    if submit:
        with st.spinner("Generating SQL Query..."):
            template = """
                 Create a SQL query snippet using the below text:
                 ```
                     {text_input}
                 ```
                 I just want a SQL Query
            """
            formatted_template = template.format(text_input=text_input)
            response = model.generate_content(formatted_template)
            sql_query = response.text

            sql_query = sql_query.strip().lstrip("```sql").rstrip("```")
            exp=cursor.execute(sql_query)
            result=cursor.fetchall()
            expected_output = """
                             ```
                                 {result}
                             ```
                             Provide sample tabular Response with no explanation.
                        """
            expected_output_formatted = expected_output.format(result=result)
            eoutput = model.generate_content(expected_output_formatted)
            explanation = """
                Explain this SQL Query:
                ```
                {sql_query}
                ```
                Please provide with simplest explanation.
            """
            explanation_formatted = explanation.format(sql_query=sql_query)
            explanation=model.generate_content(explanation_formatted)
            explanation=explanation.text
            with st.container():
                st.success("SQL Query Generated Successfully! Here is your Query Below:")
                st.code(sql_query, language="sql")
                st.success("Expected Output of this SQL Query will be:")
                st.markdown(eoutput.text) 
                st.success("Explanation of this Query")
                st.markdown(explanation)  


func()
