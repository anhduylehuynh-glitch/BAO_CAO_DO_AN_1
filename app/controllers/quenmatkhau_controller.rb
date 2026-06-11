class QuenmatkhauController < ApplicationController

    def quenmk
    end

    # ===== GỬI OTP =====
    def gui_otp
        email = params[:email]

        user = Nguoidung.find_by(email: email)

        if user.nil?
            flash[:error] = "Email không tồn tại!"
            redirect_to quenmatkhau_path
            return
        end

        otp = rand(100000..999999)

        session[:otp] = otp
        session[:reset_email] = email

        begin
            Rails.logger.info "SMTP USER=#{ENV['GMAIL_USERNAME']}"
            Rails.logger.info "SMTP PASS EXISTS=#{ENV['GMAIL_APP_PASSWORD'].present?}"
            OtpMailer.gui_otp(email, otp).deliver_now

            flash[:success] = "Đã gửi mã OTP về email"

        rescue => e
            Rails.logger.error "MAIL ERROR: #{e.class}"
            Rails.logger.error e.message
            Rails.logger.error e.backtrace.first(10).join("\n")

            flash[:error] = "Lỗi gửi mail: #{e.class}"
        end

        redirect_to quenmatkhau_path
    end

    # ===== KIỂM TRA OTP =====
    def xac_nhan_otp

        otp = params[:otp].join

        if otp == session[:otp].to_s

            session[:otp_verified] = true

            redirect_to quenmatkhau_path(step: "reset")

        else
            flash[:error] = "Mã OTP không đúng!"
            redirect_to quenmatkhau_path(step: "otp")
        end
    end

    # ===== ĐẶT LẠI MẬT KHẨU =====
    def dat_lai_mat_khau

        unless session[:otp_verified]
            redirect_to quenmatkhau_path
            return
        end

        username = params[:username]
        password = params[:password]

        user = Nguoidung.find_by(email: session[:reset_email])

        user.USERNAME = username
        user.MATKHAU = password

        if user.save

            session.delete(:otp)
            session.delete(:reset_email)
            session.delete(:otp_verified)

            flash[:success] = "Đổi mật khẩu thành công"

            redirect_to dangnhap_dangnhap_path

        else
            flash[:error] = "Có lỗi xảy ra"
            redirect_to quenmatkhau_path(step: "reset")
        end
    end
end