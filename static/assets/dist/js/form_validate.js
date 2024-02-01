jQuery("#admin-login-page-form").validate({
    rules:{
        email:{
            required:true,
            email:true
        },
        password:"required"
    },messages:{
        email:{
            required:"Please Enter Email",
            email:"Please Enter A Valid Email"
        },
        password:"Please Enter Your Password"
    }
});

jQuery("#change-password-form").validate({
    rules:{
        new_pass:{
            required:true
        },
        confirm_new_pass:{
            required:true, 
            equalTo: "#new_pass"
        }
    },messages:{
        new_pass:{
            required:"Please Enter New Password",
        },
        confirm_new_pass:{
            required:"Please Enter Confirm Password",
            equalTo:"Password And Confirm Password Not Matched"
        }
    }
});

jQuery("#cust_send_notify_form").validate({
    rules:{
        title:{
            required:true,
            maxlength:100
        }, 
        message:{
            required:true,
            maxlength:250
        }
    },messages:{
        title:{
            required:"Please Enter Title",
            maxlength:"Max length should be 100 characters"
        },
        message:{
            required:"Please Enter Message",
            maxlength:"Max length should be 250 characters"
        }
    }
});

jQuery("#category-add-form").validate({
    rules:{
        category:"required",
        catImage:"required",
        'subCatName[]':{
            required: true
        }
    
    },messages:{
        category:"Please Enter Category Name",
        catImage:"Please Choose Category Icon",
        'subCatName[]':{
            required:"Please Enter Sub Category Name"
        }
    }
});

jQuery("#edit-category-add-form").validate({
    rules:{
        category:"required",
    },messages:{
        category:"Please Enter Category Name"
    }
});


jQuery("#subcategory-add-form").validate({
    rules:{
        subcategory:"required"
    },messages:{
        subcategory:"Please Enter Sub Category Name"
    }
});

jQuery("#edit-subcategory-add-form").validate({
    rules:{
        subcategory:"required"
    },messages:{
        subcategory:"Please Enter Sub Category Name"
    }
});

jQuery("#company-add-form").validate({
    rules:{
        name:"required",
        address:"required",
        compImage:"required"
    },messages:{
        name:"Please Enter Sub Category Name",
        address:"Please Enter Address",
        compImage:"Please Enter Company Logo"
    }
});
jQuery("#company-edit-form").validate({
    rules:{
        name:"required",
        address:"required"
    },messages:{
        name:"Please Enter Sub Category Name",
        address:"Please Enter Address"
    }
});