# RSU-Commissioning
  Python Script for RSU Commissioning

# Install Libraries
  pip3 install paramiko
  pip3 install paramiko
  
# Running the script options from Laptop Terminal Window - Notice the FCC Approval Status
  python3 commission.py 192.168.0.54 Sdsm On - CV2X Radios ON
  python3 commission.py 192.168.0.54 Sdsm Off - CV2X Radios OFF
  python3 commission.py 192.168.0.54 Psm - On - CV2X Radios ON
  python3 commission.py 192.168.0.54 Psm - Off - CV2X Radios OFF
  
# Testing Performed - Linux Ubuntu and Windows 10
    # Disabling the SDSM Feature
    1. Connect to the RSU Devcie using the FireFly GUI Control
    2. Change ALL key Parameters to be in different values from the commisioning mode.
    3. SAVE and APPLY
    4. RUN the Injector Test Script and Validate that the SDSM does not operate
      * NO Objects Display in Tablet Foresight App
  # Enabling the SDSM Features
    1. RUN the commission.py script with SDSM and Radio ON option
    2. Connecting to the RSU Devcie using the FireFly GUI Control
    3. Validate all the key GUI Control Parameters of the V2X Stack enabled for SDSM
    4. RUN the Injector Test Script and Validate that the SDSM feature operates
      * Objects Display in Tablet Foresight App
# Changing the Password
  1. Changing the Password to Comply with the validation requirements
      5 < length < 15
      1 lower cae letter
      1 upper case letter
      1 number
      1 special character
  2. Hidding the Password Information achived. 
  3. ReEnter of password incase of mismatch between Enter and Retype
