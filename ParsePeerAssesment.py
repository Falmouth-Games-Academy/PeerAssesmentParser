from bs4 import BeautifulSoup
import xlsxwriter
from os import walk

#walk a directoy which contains a series of html files
html_src_path="PeerAssessments"
qualitive_xls_dest_path="Peer-Qualitive.xlsx"
quantitve_xls_dest_path="Peer-Quantitive.xlsx"

assesment_form_html_id="mform3"
checkbox_type="radio"
criteria_class="fitem description rubric"

feedback_class="no-overflow"

#Read a directory and get a list of filename which end in html
def get_html_files(path):
    print("Reading files in "+path)
    html_file_names=[]
    for (dirpath, dirnames,filenames) in walk(path):
        for filename in filenames:
            if (filename.endswith(".html")):
                html_file_names.append(html_src_path+"/"+filename)
    
    return html_file_names

#write a spreadsheet
def write_quantitve_data(filenames,dest_filename):
    workbook=xlsxwriter.Workbook(dest_filename)
    worksheet=workbook.add_worksheet()
    file_contents=""
    for filename in filenames:
        with open(filename,'r',encoding='utf8') as file:
            file_contents=file.read()
        soup=BeautifulSoup(file_contents,'html.parser')

        #get headings
        heading_divs=soup.find_all('div',class_=criteria_class)
        heading_set=set()
        for heading_div in heading_divs:
            heading_set.add(heading_div.p.get_text())
        
        #get all radio boxes
        radio_values=[]
        radio_box_html=soup.find_all('input',type="radio")
        for radio_box in radio_box_html:
            radio_values.append(radio_box.has_attr('checked'))
        
        #write to a spreadsheet the radio values, ensure that we
        #under the correct heading
        radio_count=0
        row_index=1
        column_index=1
        for radio_value in radio_values:
            if (radio_count>(len(heading_set)-1)):
                radio_count=0
                column_index=1
                row_index=row_index+1

            worksheet.write(row_index,column_index,radio_value)
            column_index=column_index+1
            radio_count=radio_count+1

        #write headings into sheet
        worksheet.write_row('B1',heading_set)
        
    workbook.close()

def write_qualitive_data(filenames,dest_filename):
    workbook=xlsxwriter.Workbook(dest_filename)
    worksheet=workbook.add_worksheet()
    file_contents=""
    for filename in filenames:
        with open(filename,'r',encoding='utf8') as file:
            file_contents=file.read()
        
        soup=BeautifulSoup(file_contents,'html.parser')
        #get headings
        feedback_divs=soup.find_all('div',class_=feedback_class)
        row_index=0
        for feedback_div in feedback_divs:
            worksheet.write_string(row_index,0,feedback_div.get_text())
            row_index=row_index+1

        
    workbook.close()



files_to_parse=get_html_files(html_src_path)
write_quantitve_data(files_to_parse,quantitve_xls_dest_path)
write_qualitive_data(files_to_parse,qualitive_xls_dest_path)

