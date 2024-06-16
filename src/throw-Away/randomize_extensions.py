import random

chrome = [

'https://chrome.google.com/webstore/detail/adblock-plus-free-ad-bloc/cfhdojbkjhnklbpkdaibdccddilifddb' ,
'https://chrome.google.com/webstore/detail/google-docs-offline/ghbmnnjooekpmoecnnnilnnbdlolhkhi' ,
'https://chrome.google.com/webstore/detail/google-mail-checker/mihcahmgecmbnbcchbopgniflfhgnkff',
'https://chrome.google.com/webstore/detail/todoist-for-chrome/jldhpllghnbhlbpcmnajkpdmadaolakh',
'https://chrome.google.com/webstore/detail/toggl-track-productivity/oejgccbfbmkkpaidnkphaiaecficdnfn?hl=en',
'https://chrome.google.com/webstore/detail/pushbullet/chlffgpmiacpedhhbkiomidkjlcfhogd',
'https://chrome.google.com/webstore/detail/bitmoji/bfgdeiadkckfbkeigkoncpdieiiefpig',
'https://chrome.google.com/webstore/detail/save-to-pocket/niloccemoadcdkdjlinkgdfekeahmflj?hl=en',
'https://chrome.google.com/webstore/detail/google-translate/aapbdbdomjkkjkaonfhkkikfgjllcleb',
'https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd',
'https://chrome.google.com/webstore/detail/honey-automatic-coupons-r/bmnlcjabgnpnenekpadlanbbkooimhnj',
'https://chrome.google.com/webstore/detail/keepa-amazon-price-tracke/neebplgakaahbhdphmkckjjcegoiijjo',
'https://chrome.google.com/webstore/detail/pinterest-save-button/gpdjojdkbbmdfjfahjcgigfpmkopogic?hl=en',
'https://chrome.google.com/webstore/detail/save-to-facebook/jmfikkaogpplgnfjmbjdpalkhclendgd',
'https://chrome.google.com/webstore/detail/avast-online-security-pri/gomekmidlodglbbmalcneegieacbdmki?hl=en',
'https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm',
'https://chrome.google.com/webstore/detail/grammarly-grammar-checker/kbfnbcaeplbcioakkpcpgfkobkghlhen',
'https://chrome.google.com/webstore/detail/google-dictionary-by-goog/mgijmajocgfcbeboacabfgobmjgjcoja',
'https://chrome.google.com/webstore/detail/hover-zoom%2B/pccckmaobkjjboncdfnnofkonhgpceea',
'https://chrome.google.com/webstore/detail/dark-reader/eimadpbcbfnmbkopoojfekhnkhdbieeh',
'https://chrome.google.com/webstore/detail/google-scholar-button/ldipcbpaocekfooobnbcddclnhejkcpn',
'https://chrome.google.com/webstore/detail/speedtest-by-ookla/pgjjikdiikihdfpoppgaidccahalehjh'
]


mozilla = [
    
'https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=recommended_fallback',
'https://addons.mozilla.org/en-US/firefox/addon/ghostery/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=featured',
'https://addons.mozilla.org/en-US/firefox/addon/search_by_image/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=featured',
'https://addons.mozilla.org/en-US/firefox/addon/google-search-fixer/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=featured',
'https://addons.mozilla.org/en-US/firefox/addon/toggl-button-time-tracker/',
'https://addons.mozilla.org/en-US/firefox/addon/pushbullet/',
'https://addons.mozilla.org/en-US/firefox/addon/to-google-translate/',
'https://addons.mozilla.org/en-US/firefox/addon/lastpass-password-manager/',
'https://addons.mozilla.org/en-US/firefox/addon/honey/',
'https://addons.mozilla.org/en-US/firefox/addon/keepa/',
'https://addons.mozilla.org/en-US/firefox/addon/canvasblocker/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=homepage-primary-hero',
'https://addons.mozilla.org/en-US/firefox/addon/pinterest/',
'https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/',
'https://addons.mozilla.org/en-US/firefox/addon/dictionary-anyvhere/',
'https://addons.mozilla.org/en-US/firefox/addon/hover-zoom-for-firefox/',
'https://addons.mozilla.org/en-US/firefox/addon/darkreader/',
'https://addons.mozilla.org/en-US/firefox/addon/google-scholar-button/',
'https://addons.mozilla.org/en-US/firefox/addon/facebook-container/',
'https://addons.mozilla.org/en-US/firefox/addon/avast-safeprice/',
'https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/'

]
with open ('profiles.txt', 'w') as f:
    for i in range(15):

        number_of_elements = random.randint(3, 6)
        result_list = random.sample(chrome, number_of_elements)

        for url in result_list:
            components = url.split('/')
            phrase = components[-2]
            f.write(phrase + '\n')
            print(phrase)
           
        f.write('==============================================' + '\n')
        f.write('==============================================' + '\n')
        print('==============================================')


