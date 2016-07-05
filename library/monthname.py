import datetime

## date to folder name converter function
# @return date in YYYY.mmMMM.dd format
def monthname():
    todaydetail = datetime.datetime.today()
    mnum=todaydetail.strftime("%m")
    mname=""
    if mnum == "01":
        mname="Jan"
    elif mnum == "02":
        mname="Feb"
    elif mnum == "03":
        mname="Mar"
    elif mnum == "04":
        mname="Apr"
    elif mnum == "05":
        mname="May"
    elif mnum == "06":
        mname="Jun"
    elif mnum == "07":
        mname="Jul"
    elif mnum == "08":
        mname="Aug"
    elif mnum == "09":
        mname="Sep"
    elif mnum == "10":
        mname="Oct"
    elif mnum == "11":
        mname="Nov"
    elif mnum == "12":
        mname="Dec"
        
    basename=todaydetail.strftime("%Y.%m")+mname+todaydetail.strftime(".%d")
    return basename
    
if __name__ == "__main__":
    print "this file returns directory name based on date of today."
    print monthname()