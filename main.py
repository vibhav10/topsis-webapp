import streamlit as st
import pandas as pd
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders



def calculate_topsis_rank(dataframe, weight_vector, criteria_vector, output_path):
    # Normalize the dataframe columns
    normalized_data = dataframe.iloc[:, 1:].div(dataframe.iloc[:, 1:].pow(2).sum(axis=0).pow(0.5), axis=1)
    
    # Apply weight vector to the normalized data
    weighted_data = normalized_data.mul(weight_vector, axis=1)
    
    # Determine the ideal best and worst solutions
    ideal_best = []
    ideal_worst = []
    for i in range(weighted_data.shape[1]):
        if criteria_vector[i] == '-':
            ideal_best.append(weighted_data.iloc[:, i].min())
            ideal_worst.append(weighted_data.iloc[:, i].max())
        else:
            ideal_best.append(weighted_data.iloc[:, i].max())
            ideal_worst.append(weighted_data.iloc[:, i].min())
    
    # Calculate the separation measure for each solution from the ideal best and worst solutions
    s_best = []
    s_worst = []
    for i in range(weighted_data.shape[0]):
        s_best.append(((weighted_data.iloc[i, :] - ideal_best) ** 2).sum() ** 0.5)
        s_worst.append(((weighted_data.iloc[i, :] - ideal_worst) ** 2).sum() ** 0.5)
    
    # Calculate the TOPSIS score and rank for each solution
    topsis_score = [x / (x + y) for x, y in zip(s_worst, s_best)]
    sorted_scores = sorted(topsis_score, reverse=True)
    topsis_rank = [sorted_scores.index(x) + 1 for x in topsis_score]
    
    # Add the TOPSIS score and rank columns to the dataframe
    dataframe = dataframe.assign(topsis_score=topsis_score, topsis_rank=topsis_rank)
    dataframe = dataframe.rename(columns={'topsis_score': 'TOPSIS Score', 'topsis_rank': 'Rank'})

    return dataframe





#heading
st.title("Vibhav Shukla - 102003772 - Topsis Module")

#make a form
with st.form(key='my_form'):

    #uploading file (csv file)
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    #input weights array
    weights = st.text_input("Enter weights array")


    #input impact array
    impacts = st.text_input("Enter impacts array")

    #input email
    email = st.text_input("Enter email")

    #name of output file
    output_file = st.text_input("Enter name of output file")

    #submit button
    submitted = st.form_submit_button(label='Submit')

    #if submit button is clicked
    if submitted:
        #read the csv file
        df = pd.read_csv(uploaded_file)

        if weights.__contains__(',') == False:
            st.write("Weights should be separated by comma")
        weights = weights.split(',')
        weights = [float(x) for x in weights]
        if(len(weights) != df.shape[1]-1):
            st.write("Number of weights should be " + str(df.shape[1]-1))
        if impacts.__contains__(',') == False:
            st.write("Impact should be separated by comma")
        impacts = impacts.split(',')
        if(len(impacts) != df.shape[1]-1):
            st.write("Number of impact should be " + str(df.shape[1]-1))
        for c in impacts:
            if  c not in ['+', '-']:
                st.write("Impact should be either + or -")
        if output_file.__contains__('.csv') == False:
            st.write("Result file should be csv")
        
        #calculate the topsis using function
        dataframe = calculate_topsis_rank(df, weights, impacts, output_file)

        #write the result to csv file
        dataframe.to_csv(output_file, index=False)
        result_file = output_file

        #send email
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "vibhav.1507@gmail.com"  # Enter your address
        receiver_email = email  # Enter receiver address

            # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = "vibhav.1507@gmail.com"
        message["To"] = receiver_email
        message["Subject"] = "Topsis Final CSV Attachment"

            # Add body to email
        message.attach(MIMEText("Please find the attached CSV file.", "plain"))

            # Open PDF file in bynary
        with open(result_file, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload((attachment).read())

            # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

            # Add header with pdf name
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={result_file}",
        )

            # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

            # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, PASSWORD)
            server.sendmail(sender_email, receiver_email, text)



        
