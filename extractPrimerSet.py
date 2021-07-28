#!/usr/bin/env python
# coding: utf-8

# In[3]:


from selenium import webdriver


# In[6]:

def presetDrivers():
    driver = webdriver.Chrome('C:/Temp/chromedriver.exe')
    driver2 = webdriver.Chrome('C:/Temp/chromedriver.exe')
    driver3 = webdriver.Chrome('C:/Temp/chromedriver.exe')
    driver4 = webdriver.Chrome('C:/Temp/chromedriver.exe')

    url = 'https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=chr1%3A220798852%2D220798852&hgsid=1134239473_iguaizUfyH8Ncad2mvmOA0Z0YUXH'
    driver.get(url)
    driver3.get('https://primer3.ut.ee/')
    
    return (driver, driver2, driver3, driver4)


# In[7]:


##preset General Primer Picking conditions 한번만 하면 됨
def preset_Primer3(driver3, pri_minSize = 20, pri_minTm = 58, prod_size = '150-250', returnN = 50):
    driver3.get('https://primer3.ut.ee/')
    xpath6 = '/html/body/form/table[7]/tbody/tr[1]/td[2]/input'
    xpath7 = '/html/body/form/table[7]/tbody/tr[2]/td[2]/input'
    xpath8 = '/html/body/form/table[8]/tbody/tr/td/input'
    xpath9 = '/html/body/form/table[9]/tbody/tr[1]/td[2]/input'
    driver3.find_element_by_xpath(xpath6).clear()
    driver3.find_element_by_xpath(xpath6).send_keys(pri_minSize)
    driver3.find_element_by_xpath(xpath7).clear()
    driver3.find_element_by_xpath(xpath7).send_keys(pri_minTm)
    driver3.find_element_by_xpath(xpath8).clear()
    driver3.find_element_by_xpath(xpath8).send_keys(prod_size)
    driver3.find_element_by_xpath(xpath9).clear()
    driver3.find_element_by_xpath(xpath9).send_keys(returnN)
    
    return None


# In[ ]:


def extractPrimer(gene_location):
#returns ((left_strt, right_end), insert_size, (F_primer,R_primer), (p1_char, p2_char))


# In[ ]:


##search location on Genome browser
    xpath = "//input[@class='positionInput ui-autocomplete-input']"
    input_genepos = driver.find_element_by_xpath(xpath)
    input_genepos.clear()

    #######input location here###############
    input_genepos.send_keys(gene_location)
    #########################################

    xpath2 = "/html/body/form[2]/center/input[4]"
    submit_btn = driver.find_element_by_xpath(xpath2)
    submit_btn.click()


# In[ ]:


##'Get DNA' page
    xpath3  = "/html/body/form[1]/center/div/div[1]/div/div/div[2]/div/div/ul/li[8]/ul/li[2]/a"
    seqUrl = driver.find_element_by_xpath(xpath3).get_attribute('href')
    print(seqUrl)
    driver2.get(seqUrl)
    xpath4 = '//input[@id="submit"]'
    getDNA_btn = driver2.find_element_by_xpath(xpath4)
    getDNA_btn.click()


# In[ ]:


##get ~1000bp sequence
    xpath5 = "/html/body/pre"
    localDNA = driver2.find_element_by_xpath(xpath5)
    only_localDNA = "\n".join(localDNA.text.split("\n")[1:])


# In[ ]:


##get list of all primers
    xpath11 = '/html/body/pre[1]'
    temp_text = driver3.find_element_by_xpath(xpath11).text.split("ADDITIONAL OLIGOS")[1].strip().split("Statistics")[0].split("\n")[1:]
    temp_text=list(filter(None, temp_text))
    primers = []

    for i in range(len(temp_text)//3):
        temp_list1 = list(filter(None, temp_text[3*i].split(' ')))[1:]
        temp_list2 = list(filter(None, temp_text[3*i+1].split(' ')))
        primers.append((temp_list1, temp_list2))

    driver3.execute_script("window.history.go(-1)") #back to primer3 mainpage

    print(primers)


# In[ ]:


    exists = 0
    t = 0
    while (t < len(primers)):
        l_st = int(primers[t][0][2])
        r_st = int(primers[t][1][2])
        ##this part needs validation##
        if ((l_st<500 and l_st>=350) and (r_st<=650 and r_st>500)):
            ######################
            driver4.get('https://genome.ucsc.edu/cgi-bin/hgBlat')
            path12 = '/html/body/table/tbody/tr/td/div[1]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/form/table/tbody/tr[3]/td/textarea'
            BLAT_box = driver4.find_element_by_xpath(xpath12)
            xpath13 = '/html/body/table/tbody/tr/td/div[1]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/form/table/tbody/tr[4]/td[2]/input[1]'
            BLAT_btn = driver4.find_element_by_xpath(xpath13)
            xpath14 = '/html/body/table/tbody/tr/td/div[1]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/form/table/tbody/tr[4]/td[2]/input[3]'
            clear_btn = driver4.find_element_by_xpath(xpath14)
            BLAT_box.send_keys("%s\n\n%s" % (primers[t][0][-1],primers[t][1][-1]))
            BLAT_btn.click()
            ######################
            xpath15 = '//*[@id="firstSection"]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div[2]/pre'
            BLAT_output = driver4.find_element_by_xpath(xpath15).text.split('-----------------------------------------------------------------------------------------------')[1].split("\n")[1:]
            #print(BLAT_output)
            if (len(BLAT_output)==2):
                F_primer = primers[t][0][-1]
                R_primer = primers[t][1][-1]
                print("%s and %s is the perfect primer!" % (F_primer,R_primer))
                pr1_list = list(filter(None, BLAT_output[0].split(' ')))[3:]
                pr2_list = list(filter(None, b = BLAT_output[1].split(' ')))[3:]
                if (pr1_list[6]=='+'):
                    left_strt = int(pr1_list[-2])+1
                    right_end = int(pr2_list[-3])-1
                    #read_length = int(p2_list[-3])-int(p1_list[-2])-2
                else:
                    left_strt = int(pr2_list[-2])+1
                    right_end = int(pr1_list[-3])-1
                    #read_length = int(p1_list[-3])-int(p2_list[-2])-2
                insert_size = right_end - left_strt
                print("insert size is %s" % (insert_size))
                print("%s th of picked primer" % (t+1))
                p1_char = "   ".join(primers[t][0][3:9])
                p2_char = "   ".join(primers[t][1][3:9])
                print("Characteristics: %s, %s" % (p1_char, p2_char))
                exists = 1
                return (True, (left_strt, right_end), insert_size, (F_primer,R_primer), (p1_char, p2_char))
                      #insert size 사실 없어도 될듯
                break
        t+=1

    if (exists == 0):
        print("no good primer")
        return (False)

