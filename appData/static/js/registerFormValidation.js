function pairVerification(element1, element2, errorElement){
    if (element1.val() == element2.val()){
        element1.removeClass('border-danger');
        element2.removeClass('border-danger');
        errorElement.css("display", "none");
        return true
    }
    else{
        element1.addClass('border-danger');
        element2.addClass('border-danger');
        errorElement.css("display", "block");
        return false
    }
}

function isEmptyVerification(checkElement, errorElement){
    if(checkElement.val() != '' ){
        checkElement.removeClass('border-danger');
        errorElement.css("display", "none");
        return true
    }
    else{
        checkElement.addClass('border-danger');
        errorElement.css("display", "block");
        return false
    }
}


function isValueAEmail(checkElement, errorElement){
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(checkElement.val())){
        checkElement.removeClass('border-danger');
        errorElement.css("display", "none");
        return true
    }
    else{
        checkElement.addClass('border-danger');
        errorElement.css("display", "block");
        return false
    }
}


function formValidation(){
    if(isEmptyVerification($('#login'),$('#loginErrorEmpty'))){
        if (isEmptyVerification($('#email'),$('#emailErrorEmpty'))){
            if(isEmptyVerification($('#emailConfirm'),$('#emailErrorEmpty'))){
                if(pairVerification($('#email'),$('#emailConfirm'),$('#emailErrorNotIdentical'))){
                    if (isValueAEmail($('#email'),$('#emailErrorNotCorrect'))){
                        if(isEmptyVerification($('#password'),$('#passwordErrorEmpty'))){
                            if(isEmptyVerification($('#passwordConfirm'),$('#passwordErrorEmpty'))){
                                if(pairVerification($('#password'),$('#passwordConfirm'),$('#passwordErrorNotIdentical'))){
                                    if($('#confirm-terms').is(':checked')){
                                        $('#register-form').submit();
                                    }
                                    else{
                                        $('#termsErrorNotCheked').css("display", "block");
                                        $('#confirm-terms').css("border","solid 1px red");
                                    }
                                }else{return}
                            }else{return}
                        }else{return}
                    }else{return}
                }else{return}
            }else{return}
        }else{return}
    }else{return}
}

function EditUserFormValidation(){
    if(pairVerification($('#newPassword'),$('#newPasswordConfirm'),$('#passwordErrorNotIdentical'))){
        $('#edit-user-form').submit();                    
    }
    else{return}
}