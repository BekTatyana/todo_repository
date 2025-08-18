import csv
import xlsxwriter


class xlsx_csv():
    def __init__(self,my_dict=None):
        if isinstance(my_dict,dict):
            my_dict = my_dict
        else:
            my_dict={}
        self.tasks = list(my_dict.values())
        self.usernames = list(my_dict.keys())

    def add_to_csv(self):
        with open('newfile.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            try:
                for i, name in enumerate(self.usernames):  
                    writer.writerow([f'Пользователь: {name}'])
               
                    for task in self.tasks[i]:
                        writer.writerow([task])
                    writer.writerow([])  
                return "Задачи успешно добавлены в CSV"
            except Exception as e:
                return f"Произошла ошибка: {str(e)}"
        
        
    def add_to_xlsx(self):
        workbook = xlsxwriter.Workbook('im_file.xlsx')
        worksheet= workbook.add_worksheet('Я лист')
        row=1
        col = 0
        try:
            for i, name in enumerate(self.usernames):
                worksheet.write(0,col, name)  
                row = 1
                for task in self.tasks[i]:    
                    worksheet.write(row,col,task)
                    row+=1
                col+=1
                
            workbook.close()
            return "Задачи успешно добавлены в Xlsx"
        except Exception:
            return "Произошла ошибка при добавлении задач в Xlsx "
        


