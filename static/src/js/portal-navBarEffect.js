

$(document).ready(function(){
    $('#btn-selfInfo, #btn-visitor, #btn-vagas, #btn-vehicle, #btn-qrcode').removeClass('bg-success');

    let navBarId = sessionStorage.getItem('@navBarId');

    const url = window.location.href.split('/')
    const page = url[url.length-1]

    if(!navBarId){
        navBarId = 'null'
    }

    if(navBarId != 'null'){
        if(page == 'profile'){
            $('#' + navBarId).addClass('bg-success');
            console.log('x')
        }
        if(page == 'visitor'){
            $('#' + navBarId).addClass('bg-success');
        }
        if(page == 'vagas'){
            $('#' + navBarId).addClass('bg-success');
        }
        if(page == 'veiculos'){
            $('#' + navBarId).addClass('bg-success'); 
        }
        if(page == 'qrcode'){
            $('#' + navBarId).addClass('bg-success'); 
        }  

    }else { 

        if(page == 'profile'){ 
            $("#btn-selfInfo").addClass("bg-success"); 

        } else if (page == "visitor") { 

            $("#btn-visitor").addClass("bg-success"); 

        } else if (page == "vagas") { 

            $("#btn-vagas").addClass("bg-success");  

        } else if (page == "veiculos") { 

            $("#btn-vehicle").addClass("bg-success"); 

        } else if (page == "qrcode" ){

            $("#btn-qrcode").addClass("bg-success");  
        }

     };   

     $('#btn-selfInfo, #btn-visitor, #btn-vagas, #btn-vehicle, #btn-qrcode').click(function(){  
         $('#btn-selfInfo, #btn-visitor, #btn-vagas, #btn-vehicle, #btn-qrcode').removeClass('bg-success');
         $(this).addClass("bg-success");  
         sessionStorage.setItem("@navBarId", $(this).attr("id"));  

     });  																 
});