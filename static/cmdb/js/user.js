// function userSave() {
//             var data = $('#Register').serializeArray();
//             var dict = {};
//             $.each(data, function () {
//                dict[this.name] = this.value
//             });
//             //dict.username = $('#id_username').val();
//             //dict.password = $('#id_password').val();
//             //dict.photo = $('#id_photo').val();
//
//             // var sendData = new FormData();
//             // sendData.append("username",$("#id_username").val());
//             // sendData.append("password",$("#id_password").val());
//             // sendData.append("photo",$("#id_photo")[0].files[0]);
//             // sendData.append("csrfmiddlewaretoken","{{ csrf_token }}");
//
//             dict['csrfmiddlewaretoken'] = '{{ csrf_token }}';
//             $.ajax(
//                 {
//                     url: '/user/user_save',
//                     type: 'post',
//                     data: sendData,
//                     //processData : false, // 告诉jQuery不要去处理发送的数据
//                     //contentType : false, // 告诉jQuery不要去设置Content-Type请求头
//                     success: function (data) {
//                         console.log(data);
//                         if(data.status == 'success'){
//                             $('.top-right').notify({
//                                 message: {text:data.data},
//                                 type: "success",
//                             }).show();
//                         }else {
//                             $('.top-right').notify({
//                                 message: {text:data.data},
//                                 type: "danger",
//                             }).show();
//                         }
//                     },
//                     error: function (error) {
//                         $('.top-right').notify({
//                             message: {text:error.data},
//                             type: "danger",
//                         }).show();
//                     }
//                 }
//             )
//         }
$(function () {
    //处理AJAX CRSF认证开始，此方式使用js单独写在文件里的情况
    jQuery(document).ajaxSend(function (event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }

        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });
    //处理AJAX CRSF认证结束

    //用户注册表单验证
    $('#Register').bootstrapValidator({
        message: 'This value is not valid',
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            username: {
                message: '用户名验证失败',

                validators: {
                    notEmpty: {
                        message: '用户名不能为空'
                    },
                    stringLength: {
                        min: 6,
                        max: 32,
                        message: '用户名长度必须在6到32之间'
                    },
                    regexp: {
                        regexp: /^[a-zA-Z0-9_]+$/,
                        message: '用户名只能包含大写、小写、数字和下划线'
                    },
                    defferent: {
                        field: 'password',
                        message: '用户名不允许和密码相同'
                    },
                    //ajax方式验证用户名是否已注册
                    threshold: 6, //有6字符以上才发送ajax请求
                    remote: {
                        type: 'POST',
                        url: '/user/userValid/',
                        data: {
                            username: function () {
                                return $('#id_username').val();
                            }
                            //下面这种方式只适合js写在html页面中的情况
                            //csrfmiddlewaretoken:'{{ csrf_token }}'
                        },
                        delay: 1000,  //每输入一个字符，就发ajax请求，服务器压力还是太大，设置1秒发送一次ajax（默认输入一个字符，提交一次，服务器压力太大）
                        message: '用户名已存在'
                    }
                }
            },
            password: {
                validators: {
                    notEmpty: {
                        message: '密码不能为空'
                    },
                    stringLength: {
                        min: 6,
                        max: 32,
                        message: '密码长度必须在6到32之间'
                    },
                    regexp: {
                        regexp: /^(?=.*\d)(?=.*[a-zA-Z])(?=.*[~!@#$%^&*.])[\da-zA-Z~!@#$%^&*.]+$/,
                        message: '密码必须包含数字、字母和特殊字符'
                    },
                    defferent: {
                        field: 'username',
                        message: '密码不允许和用户名相同'
                    }
                }
            }
        }
    });

    //用户注册提交按钮
    // $('#UserSubmit').click(
    //     function () {
    //         userSave();
    //     }
    // )

});
