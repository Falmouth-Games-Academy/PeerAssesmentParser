from bs4 import BeautifulSoup
import xlsxwriter
import hashlib
from os import walk

#walk a directoy which contains a series of html files
html_src_path="PeerAssessments"
qualitive_xls_dest_path="Peer-Qualitive.xlsx"
quantitve_xls_dest_path="Peer-Quantitive.xlsx"

assesment_form_html_id="mform3"
checkbox_type="radio"
criteria_class="fitem description rubric"

feedback_class="no-overflow"
no_of_criteria=5

grade_class="grade"
username_class="fullname"

assessed_text="Not assessed yet"

#Read a directory and get a list of filename which end in html
def get_html_files(path):
    print("Reading files in "+path)
    html_file_names=[]
    for (dirpath, dirnames,filenames) in walk(path):
        for filename in filenames:
            if (filename.endswith(".html")):
                html_file_names.append(html_src_path+"/"+filename)
    
    return html_file_names

def parse_feedback_file(file_contents,worksheet,start_row_no):
    pass
    
#write a spreadsheet
def parse_feedback_files(filenames,dest_filename):
    workbook=xlsxwriter.Workbook(dest_filename)
    worksheet=workbook.add_worksheet()
    file_contents=""
    for filename in filenames:
        with open(filename,'r',encoding='utf8') as file:
            file_contents=file.read()
        
        worksheet_name=filename
        soup=BeautifulSoup(file_contents,'html.parser')

        graded_list=[]
        graded_list=soup.find_all('div',class_=grade_class)
        print(graded_list)

        #get user names
        hashed_reviewer_list=[]
        hashed_reviewee_list=[]
        graded_count=0
        username_divs=soup.find_all('div',class_=username_class)
        hashed_reviewee_name=hashlib.md5(username_divs[0].a.get_text().encode())

        for i in range(1,len(username_divs)):
            if (graded_list[graded_count].get_text()!=assessed_text):
                hashed_username=hashlib.md5(username_divs[i].a.get_text().encode())
                hashed_reviewer_list.append(hashed_username.hexdigest())
                hashed_reviewee_list.append(hashed_reviewee_name.hexdigest())
            graded_count=graded_count+1

        #get headings
        heading_divs=soup.find_all('div',class_=criteria_class)
        heading_list=['reviewee','reviewer']
        heading_set=set()
        #print(heading_divs)
        for heading_div in heading_divs:
            heading_text=heading_div.get_text()
            if heading_text not in heading_set:
                heading_set.add(heading_text)
                heading_list.append(heading_text)
        
        worksheet.write_row('A1',heading_list)
        
        #get all radio boxes
        radio_values=[]
        radio_box_html=soup.find_all('input',type="radio")
        for radio_box in radio_box_html:
            radio_values.append(radio_box.has_attr('checked'))
        
        #record actual grades rather than true or false
        current_criteria_count=0
        grade_values=[]
        for radio_value in radio_values:
            if radio_value:
                grade_values.append(current_criteria_count)
            
            current_criteria_count=current_criteria_count+1
            if current_criteria_count>no_of_criteria:
                current_criteria_count=0

        #record the grade values in a spreadsheet
        current_excel_row=1
        current_excel_column=2
        current_grade_count=0
        for grade_value in grade_values:
            worksheet.write(current_excel_row,current_excel_column,grade_value)
            
            current_criteria_count=current_criteria_count+1
            current_excel_column=current_excel_column+1

            if (current_criteria_count==no_of_criteria):
                current_excel_row=current_excel_row+1
                current_excel_column=2
                current_criteria_count=0
        
        #record the usernames
        current_excel_row=1
        current_excel_column=1        
        
        for hashed_username in hashed_reviewer_list:
            worksheet.write(current_excel_row,current_excel_column,hashed_username)
            current_excel_row=current_excel_row+1

                #record the usernames
        current_excel_row=1
        current_excel_column=0        
        
        for hashed_username in hashed_reviewee_list:
            worksheet.write(current_excel_row,current_excel_column,hashed_username)
            current_excel_row=current_excel_row+1
            
        feedback_divs=soup.find_all('div',class_=feedback_class)
        current_excel_row=0
        current_excel_column=no_of_criteria+2   
        for feedback_div in feedback_divs:
            worksheet.write_string(current_excel_row,current_excel_column,feedback_div.get_text())
            current_excel_row=current_excel_row+1

    workbook.close()

files_to_parse=get_html_files(html_src_path)
parse_feedback_files(files_to_parse,quantitve_xls_dest_path)

