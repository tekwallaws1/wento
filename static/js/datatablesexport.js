// Datatables Replace Data and empty lines for Excel and PDF Both //
  function remove_tags(html) {
    html = html.replace(/<br>/g,"$br$"); 
    html = html.replace(/<div>/g,"$div$");
    html = html.replace(/(?:\r\n|\r|\n)/g, '$n$'); 

    var tmp = document.createElement("DIV"); 
    tmp.innerHTML = html; 
    html = tmp.textContent||tmp.innerText; 

    html = html.replace(/\$br\$/g,"\n"); 
    html = html.replace(/\$n\$/g,""); 
    html = html.replace(/\$div\$/g,""); 
    
    return html;
  };

  var _format = { body: function ( data, row, column, node ) { 
    // data = data.replace( /--Edit/g, "" ); 
    // data = data.replace( /--Copy/g, "" ); 
    // data = data.replace( /--Delete/g, "" ); 
    data = data.replace( /--Chat--/g, "" ); 
    data = remove_tags(data);
    
    return data;
  }};
//--End--//


// Datatables Replace Data and empty lines for Print //
  function remove_tags_print(html) {
     html = html.replace(/<br>/g,"$br$"); 
    html = html.replace(/<div>/g,"$div$");
    html = html.replace(/(?:\r\n|\r|\n)/g, '$n$'); 

    var tmp = document.createElement("DIV"); 
    tmp.innerHTML = html; 
    html = tmp.textContent||tmp.innerText; 

    html = html.replace(/\$br\$/g,"<br>"); 
    html = html.replace(/\$n\$/g,"\n"); 
    html = html.replace(/\$div\$/g,"<div>"); 
    
    return html;
  };

  var formatprint = { body: function ( data, row, column, node ) { 
    data = data.replace( /--Chat--/g, "" ); 
    data = remove_tags_print(data);
    
    return data;
  }};

//--End--//

// Datatables Common Properties //
  var olg =  {"sSearch": '',"sSearchPlaceholder": "Search/Filter...","sLengthMenu": "",};
  var lmenu = [ [20, 50, 100, -1], [20, 50, 100, "All"] ];

  var footer1 = (function(page, pages) {
    return {columns: ['Sree Sai Electronics',{alignment: 'right',italics: true,
    text: ['page ', { text: page.toString()},  ' of ', { text: pages.toString()}]}],margin: [40, 0]}});

  var table_header = {fillColor:'#525659',color:'#FFF',fontSize: '9',alignment: 'left',bold: true,  }
//--End--//

