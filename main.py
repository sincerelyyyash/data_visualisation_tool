import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mysql.connector

PAGE_CONFIG = {"page_title": "Data Visualization", "page_icon": "chart_with_upwards_trend:", "layout": "centered"}
st.set_page_config(**PAGE_CONFIG)

def showGraphList():
    """This function will return all the graph available"""
    graph = ["Line Chart", "Bar Chart", "Pie Chart"]
    opt = st.radio("Select to ", graph)
    return opt

def sidebar():
    global df, option, opt, columnList
    df = None
    allowedExtension = ['csv', 'xlsx']
    connection = None
    with st.sidebar:
        st.write("Choose Data Source:")
        data_source = st.radio("", ["Local File", "MySQL Database"])
        
        if data_source == "Local File":
            uploaded_file = st.file_uploader(label="Upload your csv or excel file.", type=['csv', 'xlsx'])
            if uploaded_file is not None:
                filename = uploaded_file.name
                extension = filename.split(".")[-1]
                if extension in allowedExtension:
                    df = pd.read_csv(uploaded_file)
                    columnList = df.columns.values.tolist()
                    option = st.selectbox("Select Column", columnList)
                    st.subheader("Filters ")
                    opt = showGraphList()
                else:
                    st.write("File Format is not supported")
        elif data_source == "MySQL Database":
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    database="mydatabase"
                )
                if connection.is_connected():
                    cursor = connection.cursor()
                    table_name = st.text_input("Enter table name:")
                    if table_name:
                        cursor.execute(f"SELECT * FROM {table_name}")
                        records = cursor.fetchall()
                        df = pd.DataFrame(records, columns=[i[0] for i in cursor.description])
                        columnList = df.columns.values.tolist()
                        option = st.selectbox("Select Column", columnList)
                        st.subheader("Filters ")
                        opt = showGraphList()
            except mysql.connector.Error as e:
                st.write(f"Error connecting to MySQL Database: {e}")
            finally:
                if connection is not None and connection.is_connected():
                    connection.close()
                    st.write("MySQL connection is closed")

def getIndexes(columnName, value):
    count = -1
    for i in df[columnName]:
        count += 1
        if i == value:
            return count

def mainContent():
    st.header("Visualize Your Data")
    if df is not None:
        st.write(df)
        label = f"Choose the Column To which you want to compare"
        st.header(label)
        selectOption = []
        for i in df[columnList[0]]:
            selectOption.append(i)
        selectedData = st.multiselect(f"Choose {columnList[0]} to see", selectOption)
        dataToVisualize = []
        for i in selectedData:
            index = getIndexes(columnList[0], i)
            value = df[option][index]
            if type(value) is not str:
                dataToVisualize.append(df[option][index])
            else:
                st.warning(f"The data type of {value} is not supported")
        if opt == "Line Chart":
            label = f"Line Chart for {option} is"
            st.header(label)
            st.line_chart(dataToVisualize)
        elif opt == "Bar Chart":
            label = f"Bar Chart for {option} is"
            st.header(label)
            st.bar_chart(dataToVisualize)
        elif opt == "Pie Chart":
            label = f"Pie Chart for {option} is"
            st.header(label)
            x = dataToVisualize
            fig, ax = plt.subplots()
            ax.pie(x, labels=selectedData, autopct='%.5f%%')
            st.pyplot(fig)
    else:
        st.write("There is nothing to show!! please add file or select MySQL table to visualize data")

if __name__ == "__main__":
    sidebar()
    mainContent()
