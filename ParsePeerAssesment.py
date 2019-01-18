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

#Write header
def write_header(html_soup,worksheet,start_row,start_column):
    heading_divs=html_soup.find_all('div',class_=criteria_class)
    heading_list=['reviewee','reviewer']
    heading_set=set()
    #print(heading_divs)
    for heading_div in heading_divs:
        heading_text=heading_div.get_text()
        if heading_text not in heading_set:
            heading_set.add(heading_text)
            heading_list.append(heading_text)

    heading_list.append('feedback')    
    worksheet.write_row(start_row,start_column,heading_list)

#write reviewer and reviewee data
def write_reviewee_reviewer(html_soup,worksheet,start_row,start_column):
    graded_list=[]
    graded_list=html_soup.find_all('div',class_=grade_class)

    #get user names
    hashed_reviewer_list=[]
    hashed_reviewee_list=[]
    graded_count=0
    username_divs=html_soup.find_all('div',class_=username_class)
    hashed_reviewee_name=hashlib.md5(username_divs[0].a.get_text().encode())

    for i in range(1,len(username_divs)):
        if (graded_list[graded_count].get_text()!=assessed_text):
            hashed_username=hashlib.md5(username_divs[i].a.get_text().encode())
            hashed_reviewer_list.append(hashed_username.hexdigest())
            hashed_reviewee_list.append(hashed_reviewee_name.hexdigest())
        graded_count=graded_count+1    
    
    current_excel_row=start_row
    current_excel_column=start_column+1
    for hashed_username in hashed_reviewer_list:
        worksheet.write(current_excel_row,current_excel_column,hashed_username)
        current_excel_row=current_excel_row+1
    
    current_excel_row=start_row
    current_excel_column=start_column    
    for hashed_username in hashed_reviewee_list:
        worksheet.write(current_excel_row,current_excel_column,hashed_username)
        current_excel_row=current_excel_row+1


def write_grade_values(html_soup,worksheet,start_row,start_column):
    radio_values=[]
    radio_box_html=html_soup.find_all('input',type="radio")
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
    current_excel_row=start_row
    current_excel_column=start_column
    current_grade_count=0
    for grade_value in grade_values:
        worksheet.write(current_excel_row,current_excel_column,grade_value)
            
        current_criteria_count=current_criteria_count+1
        current_excel_column=current_excel_column+1

        if (current_criteria_count==no_of_criteria):
            current_excel_row=current_excel_row+1
            current_excel_column=start_column
            current_criteria_count=0
    
    return current_excel_row

def write_feedback(html_soup,worksheet,start_row):
    feedback_divs=html_soup.find_all('div',class_=feedback_class)
    current_excel_row=start_row
    current_excel_column=no_of_criteria+2   
    for i in range(1,len(feedback_divs)):
        worksheet.write_string(current_excel_row,current_excel_column,feedback_divs[i].get_text())
        current_excel_row=current_excel_row+1

#write a spreadsheet
def parse_feedback_files(filenames,dest_filename):
    workbook=xlsxwriter.Workbook(dest_filename)
    worksheet=workbook.add_worksheet()
    header_written=False
    current_row=1
    number_of_rows=1
    file_contents=""
    for filename in filenames:
        with open(filename,'r',encoding='utf8') as file:
            file_contents=file.read()
        
        
        soup=BeautifulSoup(file_contents,'html.parser')
        if not header_written:
            write_header(soup,worksheet,0,0)
            header_written=True

        write_reviewee_reviewer(soup,worksheet,number_of_rows,0)
        write_feedback(soup,worksheet,number_of_rows)
        number_of_rows=write_grade_values(soup,worksheet,number_of_rows,2)

    workbook.close()

files_to_parse=get_html_files(html_src_path)
parse_feedback_files(files_to_parse,quantitve_xls_dest_path)