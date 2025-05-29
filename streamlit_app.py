# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Add a name input box
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Start Snowpark session
# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

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
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        st.subheader(fruit_chosen + ' Nutrition Information')
        # Display JSON response in a table
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        st.stop()

    st.write(ingredients_string)

    # Construct SQL insert statement for both columns
    my_insert_stmt = (
        """insert into smoothies.public.orders (ingredients, name_on_order) """
        + """values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    )

     # Button to submit order
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
   
    # Show the SQL for debugging
    st.write(my_insert_stmt)
    st.stop()  # Pause app to verify the query is formatted correctly




