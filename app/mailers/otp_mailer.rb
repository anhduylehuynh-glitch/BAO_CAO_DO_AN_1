class OtpMailer < ApplicationMailer
    default from: "Hệ thống OTP <onboarding@resend.dev>"

    def gui_otp(email, otp)
        @otp = otp

        mail(
            to: email,
            subject: "Mã OTP xác nhận đổi mật khẩu"
        )
    end
end