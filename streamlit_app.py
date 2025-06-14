# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Add a name input box
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Start Snowpark session
cnx = st.connection("snowflake")
session = cnx.session()
# Pull both FRUIT_NAME (for display) and SEARCH_ON (for lookup) into a dataframe
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), 
    col("SEARCH_ON")
)

# Display the dataframe to verify contents
# st.dataframe(data=my_dataframe, use_container_width=True)

# Stop the app here temporarily to focus on verifying the dataframe
# st.stop()

# Get Snowpark dataframe
my_dataframe = session.table('smoothies.public.fruit_options') \
                      .select(col('FRUIT_NAME'), col('SEARCH_ON'))
# Convert to pandas
pd_df = my_dataframe.to_pandas()
# Display pandas dataframe to verify
# st.dataframe(pd_df, use_container_width=True)
# Optional: pause the app here during testing
# st.stop()

# Multiselect fruit options
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe,  # or your specific list of options
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredients_string)
    st.write("SQL statement:", my_insert_stmt)

    # Sanitize input to avoid breaking the SQL
    safe_ingredients = ingredients_string.replace("'", "''")
    safe_name = name_on_order.replace("'", "''")

    # Construct SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{safe_ingredients}', '{safe_name}')
    """

    # Button to submit order
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

    # Show the SQL for debugging
    st.write(my_insert_stmt)
    st.stop()



