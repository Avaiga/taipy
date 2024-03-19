# <center> **Collect Data**{:.color-primary} for National Population and Housing Census</center>

<br/>

<|container|

<input|class_name=card|

<|layout|columns= 1 1|gap=30px|

<district|

## **District**{:.color-primary}

<|{selected_district}|selector|lov={district_list}|on_change=on_change_district|dropdown|>
|district>

<local_level_name|

## **Local Level Name**{:.color-primary}

<|{selected_local_level}|selector|lov={local_level_name_list}|dropdown|>
|local_level_name>

|>

<|layout|columns=1 1 1 1|gap=10px|

<male|

## **Male**{: .color-primary} Population

<|{male_population}|input|label=Total Male Population|>
|male>

<female|

## **Female**{: .color-primary} Population

<|{female_population}|input|label=Total Female Population|>
|female>

<household|

## **Household**{: .color-primary} Number

<|{household_member}|input|label=Total Household Number|>
|household>

<family|

## **Family**{: .color-primary} Member

<|{family_member}|input|label=Total Family Member|>
|family>

|>

|input>

|>

<center>
<|Submit Data|button|class_name= m4 p1|>
</center>
