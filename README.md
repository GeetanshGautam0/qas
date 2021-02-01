# Quizzing Application 2.00.0x

<!-- <img align="center" src="https://cdn.pixabay.com/photo/2014/05/21/19/16/the-question-mark-350170_960_720.png"> --!>

The Quizzing Application Suite is a collection of python modules that come together to make a fairly powerful Quizzing Application.

<p float="center">
  <img src="https://raw.githubusercontent.com/GeetanshGautam-CodingMadeFun/qas-2.0/main/icons/admin_tools_64.png">
  <img src="https://raw.githubusercontent.com/GeetanshGautam-CodingMadeFun/qas-2.0/main/icons/ftsra_64.png">
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/icons/quizzing_tool_64.png?raw=true">
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/icons/themer_64.png?raw=true">
</p>

<b><h3>These include a few apps</h3></b>
<ul>
  <li>Quizzing Application Administrator Tools</li>
  <li>Quizzing Application Quizzing Form</li>
</ul>

<b><h3>Along with a few utilities</h3></b>
<ul>
  <li>Quizzing Application FTSRA (First Time Setup and Recovery Agent) Utility</li>
  <li>Quizzing Application Theming Utility</li>
</ul>

<b><h3>Updated from version 1.5, this version will contain several imporvements. A few of them include</h3></b>
<ul>
  <li>A less buggy quizzing form</li>
  <li>A keylogger to keep track of all actions committed by the quiz taker</li>
    <ul><li>Note that this keylogger only runs whilst the quiz taker is actively participating in the quiz.</li></ul>
  <li>All files will noe be encrypted</li>
  <li>More options for administrators:</li>
  <ul>
    <li>Language Settings (possible, but not confirmed)</li>
    <li>Allow quiz taker to see there score</li>
    <li>and more!</li>
  <li>Exporting scores and other human-readable files in *.pdf</li>
  <li>Faster algorithms to make your experience smoother</li>
  <li>More code, more functions, less disk space</li>
  <li>Better UI</li>
  <li>All functions of the application are logged, therefore allowing the user to debug and troubleshoot.</li>
  <li>Errors now display as there own GUI</li>
  <li>More robust than ever.</li>
  
  <li>And MUCH more....</li>

<b><h1>Changes</h1></b>

<details>
  <summary>Administrator Tools</summary>
  <p float="left">
    <b><h2>Quizzing Application Administrator Tools</h2></b>
    <!-- <img src="https://raw.githubusercontent.com/GeetanshGautam-CodingMadeFun/qas-2.0/main/icons/admin_tools_64.png"> -->
  </p>
  <ol>
  <li> Use to <b>easily</b> alter any and all settings that you may wish to change. </li>
    
  <li> UI based question addition </li>
    
  <li> The complere re-write has also enabled the quiz giver to use the characters "<strong>|</strong>" and "<strong>`</strong>" which were previously occupied by the code in order to organize questions. </li>
  </ol>
</details>

<details>
  <summary>Quizzing Form</summary>
  <b><h2>Quizzing Application Quizzing Form</h2></b>
  <ol>
  <li> A key logger has been implemented to keep track of all keyboard inputs by the user </li>
  <li> The form no longer will allow the user to temporarly exit the quizzing form and open other windows during error sequences, unlike version 1.5 and before </li>
  <li> <b>[UNCONFIRMED CHANGE]</b> Multiple choice questions will now utilize Radio Buttons for an input. </li>
  </ol>
</details>

<details>
  <summary>First Time Setup and Recovery Agent</summary>
  <b><h2>Quizzing Application FTSRA Utility</h2></b>
  <ol>
  <li> The utility should now be able to copy directories and their sub-directories </li>
  <li> The utility will noe allow the user to now overwrite <b>all</b> of their files if they choose to not do so. </li>
  <li> Added "Help Me" PDF </li>
  <li> Added internal file checks </li>
  </ol>
</details>

<details>
  <summary>Theming Utility</summary>
  <b><h2>Quizzing Application Theming Utility</h2></b>
  <ol>
    <li> Added text previews besides the button </li>
    <li> Cleaner UI than 1.xx TU </li>
    <li> Font size and font face changing for the user (size applies to buttons and paragraphs only). </li>
    <li> Minor change: the restore button will have an inverted foreground in respect to the background to ensure that it can be seen at all times. </li>
  </ol>
</details>

<ul>
<li> Note that most font-related items are not shown very well in the TU (or FTSRA) </li>
<li> Note that the UI appears glitchy when refreshing UI because of the theme applying code and the odd method of adding widgets to the app. </li>
</ul>

<b><h1>Other Notes</h1></b>
<details>
  
  <summary>FileIOHandler Performance With Different Encodings</summary>
  
  <p>Take note of the exponent labeled above the fourth graph</p>
  
  <b><h2>UTF-7</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/utf7.png?raw=true">
  
  <b><h2>UTF-8</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/utf8.png?raw=true">
  
  <b><h2>UTF-16</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/utf16%20(post-fix).png?raw=true">
  
  <b><h2>UTF-32</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/utf32%20(post-fix).png?raw=true">
  
  <b><h2>ASCII</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/ascii.png?raw=true">
  
  <b><h2>CP936</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/cp936.png?raw=true">
  
  <b><h2>EUCJP</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/eucjp.png?raw=true">
  
  <b><h2>IBM437</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/ibm437.png?raw=true">
  
  <b><h2>IBM869</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/ibm869.png?raw=true">
  
  <b><h2>ISO-2022-JP-EXT</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/iso-2022-jp-ext.png?raw=true">
  
  <b><h2>MS932</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/ms932.png?raw=true">
  
  <b><h2>L1</h2></b>
  <img src="https://github.com/GeetanshGautam-CodingMadeFun/qas-2.0/blob/main/FileIOHandler%20Performance/L1.png?raw=true">
  
</details>
