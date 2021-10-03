# FIXME add needed imports
import json
from jsonschema import validate
from matplotlib import pyplot as plt





def load_covid_data(filepath):
    try:
        # Open file via filepath
        with open(filepath,'r') as f:
            # Read each line inside the file
            my_data_string = f.read()
            # Convert json file into python object
            my_data = json.loads(my_data_string)
        return my_data
    except:
        raise FileNotFoundError('No file was found')


def rebin(binA,binB):
    # These two arrays store the age value which split below
    newA = []
    newB = []
    rebin_data = []
    # We split the data range into 2D array
    for i in range(0,len(binA)):
        ageA = binA[i].split('-')
        newA.append(ageA)     
    for i in range(0,len(binB)):
        ageB = binB[i].split('-')
        newB.append(ageB)
    
    # If there is no data or the minimum value is different, two datasets could not be rebined
    if newA[0][0]!=newB[0][0] or newA[0][1] is None or newB[0][1] is None:
        raise NotImplementedError('Error for rebin')
    else:
        i = 0
        j = 0
        # We will consider the last element later i.e '40-'
        while i <= len(newA)-2 and j <= len(newB)-2:
            '''
            If the maximum age of the age range never matches, then they are not
            able to rebin. If we found one of the maximum age is equal to the next
            maximum age of the other, that means we can sum it up to make them the 
            same age range.
            '''
            if int(newA[i][1]) < int(newB[j][1]):
                firstElement=int(newA[i][0])
                i+=1
                if int(newA[i][1]) > int(newB[j][1]):
                    raise NotImplementedError("Rebin fail")
                elif int(newA[i][1]) == int(newB[j][1]):
                    rebin_data.append(str(firstElement) + '-' + str(newA[i][1]))
                    i+=1
                    j+=1         
            elif int(newA[i][1]) > int(newB[j][1]):
                firstElement = newA[i][0]
                j+=1
                if int(newA[i][1]) < int(newB[j][1]):
                    rebin_data = null
                elif int(newA[i][1]) == int(newB[j][1]):
                    rebin_data.append(str(firstElement) + '-' + str(newA[i][1]))
                    i+=1
                    j+=1
                else:
                    rebin_data = null
            elif int(newA[i][1]) > int(newB[j][1]):
                firstElement = newA[i][0]
                j+=1
                if int(newA[i][1]) < int(newB[j][1]):
                    rebin_data=null
                elif int(newA[i][1]) == int(newB[j][1]):
                    rebin_data.append(str(firstElement) + '-' + str(newA[i][1]))
                    i+=1
                    j+=1
            else:
                rebin_data = null
        if int(newA[i][0]) == int(newB[j][0]):
            rebin_data.append(newA[i][0]+'-')
        return rebin_data
    



def cases_per_population_by_age(input_data):
    date = []
    age_range = []
    daily_data_age = []
    daily_rate = []
    result = {}
    hospitalization_age = input_data['metadata']['age_binning']['hospitalizations']
    population_age = input_data['metadata']['age_binning']['population']
    if hospitalization_age is None or population_age is None:
        raise NotImplmentedError('No age bin inside')
    # If two age bins are equal, then we don't need to rebin them.
    elif hospitalization_age == population_age:
        age_range = population_age
    else:
        age_range=rebin(hospitalization_age,population_age)
    total_population=input_data['region']['population']['age']
    # Set the key of the result which is the age range for dictionary structure
    for i in range (0,len(age_range)):
        result[age_range[i]]=[]
    for i in range (0,len(total_population)):
        if total_population[i] is None:
            print("Missing data")
            raise NotImplementedError("Missing some data here")        
    for i in input_data["evolution"].keys():
        date.append(i)    
    for i in input_data["evolution"].values():
        daily_data_age.append(i["epidemiology"]["confirmed"]["total"]["age"])
    for i in range (len(date)):
        if daily_data_age is None:
            del date[i]
        else:
            for j in range (len(age_range)):
                daily_rate.append(daily_data_age[i][j]/total_population[j])
    for i in range(len(date)):
        for j in range(len(age_range)):
            result[age_range[j]].append((date[i], daily_rate[i * len(population_age) + j]))
    return result


def hospital_vs_confirmed(input_data):
    date = []
    for i in input_data["evolution"].keys():
        date.append(i)
   
    num_hosp = []
    num_con = []
    miss_data = []
    index = 0

    try:
        for i in input_data["evolution"].values():
            if i["hospitalizations"]["hospitalized"]["new"]["all"] is not None and i["epidemiology"]["confirmed"]["new"]["all"] is not None:
                num_hosp.append(i["hospitalizations"]["hospitalized"]["new"]["all"])
                num_con.append(i["epidemiology"]["confirmed"]["new"]["all"])
            else:
                # Record the date which has missing data and remove it later
                miss_data.append(index)
            index = index + 1
        for i in range(len(miss_data)):
            # Discard the date which has missing data
            del date[miss_data[i]]   
        ratio = []
        for i in range(len(date)):
            ratio.append(num_hosp[i] / num_con[i])
    except:
        raise NotImplementedError("Missing all the data")

    result = (date, ratio)
    return result



def generate_data_plot_confirmed(input_data, sex, max_age, status):
    """
    At most one of sex or max_age allowed at a time.
    sex: only 'male' or 'female'
    max_age: sums all bins below this value, including the one it is in.
    status: 'new' or 'total' (default: 'total')
    """
    if status == 'new':
        line_style = '--'
    elif status == 'total':
        line_style = '-'
    else:
        raise NotImplementedError('Invalid status input')

    status = 'total'

    population_age = input_data["metadata"]["age_binning"]["population"]
    date = input_data['evolution'].keys()
    sex_data = []
    sum_age = 0
    sum_age_group = []
    graph_data = []
    if sex:
        line_label = '{}{}'.format(status, sex)
        if sex == 'male':
            for i in input_data["evolution"].values():
                # Set line color for male
                line_color = 'green'
                # Retrieve male data
                sex_data.append(i["epidemiology"]["confirmed"][status]["male"])
        elif sex == 'female':
            for i in input_data["evolution"].values():
                line_color = 'purple'
                sex_data.append(i["epidemiology"]["confirmed"][status]["female"])
        elif sex != 'male' and sex != 'female':
            raise NotImplementedError('Invalid input')
        graph_data = [sex_data, line_color, line_style, line_label]
        return graph_data
    
    if max_age:
        # Set color for different age range
        if max_age <= 25:
            line_color = 'green'
        if max_age <= 50:
            line_color = 'orange'
        if max_age <= 75:
            line_color = 'purple'
        else:
            line_color = 'pink'
        # Set label for max_age
        line_label = '{} younger than {}'.format(status, max_age)

        for i in date:
            for j in range (0,len(population_age)):
                sum_age = sum_age + int(input_data["evolution"][i]["epidemiology"]["confirmed"][status]["age"][j])
            sum_age_group.append(sum_age)
        graph_data = [sum_age_group, line_color, line_style, line_label]
        return graph_data



def create_confirmed_plot(input_data, sex=False, max_ages=[], status=..., save=...):
    # FIXME check that only sex or age is specified.
    fig = plt.figure(figsize=(10, 10))
    # FIXME change logic so this runs only when the sex plot is required
    date = input_data['evolution'].keys()
    status = 'total'
    
    if sex:
        typefig = 'sex'
        for sex in ['male','female']:
            plotdict = {'date':date, 'value':generate_data_plot_confirmed(input_data, sex,max_ages, status)[0]}
            line_color = generate_data_plot_confirmed(input_data, sex, max_ages,status)[1]
            line_style = generate_data_plot_confirmed(input_data, sex, max_ages,status)[2]
            line_label = generate_data_plot_confirmed(input_data, sex, max_ages,status)[3]
            plt.plot('date','value',label = line_label, color = line_color, linestyle = line_style, data = plotdict)
    elif max_ages:
        typefig = 'age'
        for age in max_ages:
            plotdict = {'date':date, 'value':generate_data_plot_confirmed(input_data, sex, age, status)[0]}
            line_color = generate_data_plot_confirmed(input_data, sex, age,status)[1]
            line_style = generate_data_plot_confirmed(input_data, sex, age,status)[2]
            line_label = generate_data_plot_confirmed(input_data, sex, age,status)[3]
            plt.plot('date','value', label = line_label, color = line_color, linestyle = line_style, data = plotdict)


    plt.xlabel("date")
    plt.ylabel("number of cases")
    plt.title("Confirmed cases solved by age " + input_data['region']['name'])
    plt.legend(loc='upper left')  
    fig.autofmt_xdate()
    plt.show()

def compute_running_average(data, window):

    # Check if the data is list or not
    if isinstance(data, list) == False:
        raise NotImplementedError('Invalid data input')
    if window % 2 == 0 or window <= 0:
        raise NotImplementedError('Window size should be odd')
    result = [None]*len(data)
    start = int((window-1)/2)
    end = int(len(data)-(window-1)/2)

    for i in range (start,end):
        window_data = [None]*window
        counter = window
        for j in range (window):
            if data[int(i-(window-1)/2+j)] is None:
                counter -= 1
                window_data[j] = 0
            else:
                window_data[j] = data[int((i-window-1)/2)+j]
        result[i] = sum(window_data)/counter
    return result
    

def simple_derivative(data):

    if isinstance(data, list) == False:
        raise NotImplementedError("Invalid data input")
    # Define result as list of none
    result = [None]*len(data)

    for i in range(1,len(data)):
        if (data[i] is not None and data[i-1] is not None):
            result[i] = data[i]-data[i-1]
    return result 


def count_high_rain_low_tests_days(input_data):

    # Extract date
    date = []
    for i in input_data["evolution"].keys():
        date.append(i)
    # Extract rainfall data
    data_rain = []
    for a in input_data["evolution"].values():
        data_rain.append(a["weather"]["rainfall"])
    # Rain increase
    day_rain_deri = simple_derivative(data_rain)
    # Extract test data
    test_data = []
    for i in input_data["evolution"].values():
        test_data.append(i["epidemiology"]["tested"]["new"]["all"])
    test_smooth = compute_running_average(test_data, 7)
    data_test_deri = simple_derivative(test_smooth)
    # Figure out the increase in rain
    rain_increase = []
    for i in range(len(date)):
        # NoneType can not be compared with integer
        if day_rain_deri[i] != None:
            if day_rain_deri[i] > 0:
                rain_increase.append(i)    
    # Figure out the increase in rain decrease in test
    test_decrease = []
    for i in rain_increase:
        if (data_test_deri[i]) != None:
            if data_test_deri[i] < 0:
                test_decrease.append(i)
    return len(test_decrease) / len(rain_increase)
