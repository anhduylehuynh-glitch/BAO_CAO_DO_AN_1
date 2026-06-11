class ThongBaoMailer < ApplicationMailer

  default from: "Hệ thống OTP <onboarding@resend.dev>"

  def trung_tuyen(thisinh, nganh)
    @thisinh = thisinh
    @nganh = nganh

    mail(
      to: @thisinh.EMAIL,
      subject: "Thông báo kết quả tuyển sinh"
    )
  end

  def khong_trung_tuyen(thisinh, nganh)
    @thisinh = thisinh
    @nganh = nganh

    mail(
      to: @thisinh.EMAIL,
      subject: "Thông báo kết quả tuyển sinh"
    )
  end

end