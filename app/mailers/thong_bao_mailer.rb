class ThongBaoMailer < ApplicationMailer

  default from: "Hệ thống OTP <onboarding@resend.dev>"

  def trung_tuyen(thisinh, nganh)
    @thisinh = thisinh
    @nganh = nganh

    mail(
      to: "anhduylehuynh@gmail.com", # Đã sửa từ @thisinh.EMAIL thành mail của bạn
      subject: "Thông báo kết quả tuyển sinh (Trúng Tuyển - Test)"
    )
  end

  def khong_trung_tuyen(thisinh, nganh)
    @thisinh = thisinh
    @nganh = nganh

    mail(
      to: "anhduylehuynh@gmail.com", # Đã sửa từ @thisinh.EMAIL thành mail của bạn
      subject: "Thông báo kết quả tuyển sinh (Không Trúng Tuyển - Test)"
    )
  end

end