class NophosoController < ApplicationController

  def nophoso
     @phuongthucxettuyens = Phuongthucxettuyen.all
     @nganhs = Nganh.all
  end

  def xac_thuc_cccd
    file = params[:filecccdt]

    if file.nil?
      render json: { success: false, message: "Không có file" }
      return
    end

    begin
      require 'net/http'
      require 'net/http/post/multipart'

      # Gọi tới API Flask chạy nền nội bộ (sử dụng localhost để tối ưu tuyến đường)
      url = URI.parse('http://127.0.0.1:5000/predict')
      
      req = Net::HTTP::Post::Multipart.new(
        url.path,
        "file" => UploadIO.new(file.tempfile, file.content_type, file.original_filename)
      )
      
      # Tăng thời gian chờ lên để an toàn trên CPU Render Free
      res = Net::HTTP.start(url.host, url.port, open_timeout: 5, read_timeout: 30) do |http|
        http.request(req)
      end

      if res.code == "200"
        render json: JSON.parse(res.body)
      else
        render json: { success: false, message: "Cổng dịch vụ AI phản hồi lỗi" }
      end

    rescue => e
      Rails.logger.error "=== KẾT NỐI API THẤT BẠI: #{e.message} ==="
      render json: { success: false, message: "Hệ thống AI đang khởi động hoặc quá tải, vui lòng thử lại sau vài giây!" }
    end
  end

  def create

    # =========================
    # USER ĐĂNG NHẬP
    # =========================

    unless current_user
      redirect_to dangnhap_dangnhap_path
      return
    end

    # =========================
    # TẠO THƯ MỤC IMAGE
    # =========================

    image_path = Rails.root.join(
      "public",
      "images"
    )

    FileUtils.mkdir_p(image_path)

    # =========================
    # HÀM LƯU FILE
    # =========================

    def save_file(file, folder)

      return nil if file.nil?

      filename =
        "#{Time.now.to_i}_#{file.original_filename}"

      path = Rails.root.join(
        "public",
        "images",
        filename
      )

      File.open(path, "wb") do |f|
        f.write(file.read)
      end

      filename
    end

    # =========================
    # LƯU FILE
    # =========================

    giayks =
      save_file(
        params[:GIAYKHAISINH],
        "images"
      )

    cccdt =
      save_file(
        params[:ANHCCCDT],
        "images"
      )

    cccds =
      save_file(
        params[:ANHCCCDS],
        "images"
      )

    hocba =
      save_file(
        params[:ANHHOCBA],
        "images"
      )

    giaytokhac =
      save_file(
        params[:ANHGIAYTOKHAC],
        "images"
      )

    # =========================
    # TẠO THÍ SINH
    # =========================

    thisinh = Thisinh.create(

      IDNGUOIDUNG:
        current_user.IDNGUOIDUNG,

      HOTENTS:
        params[:HOTENTS],

      GIOITINH:
        params[:GIOITINH],

      NOISINH:
        params[:NOISINH],

      DANTOC:
        params[:DANTOC],

      NGAYSINH:
        params[:NGAYSINH],

      GIAYKHAISINH:
        giayks,

      SOCCCD:
        params[:SOCCCD],

      ANHCCCDT:
        cccdt,

      ANHCCCDS:
        cccds,

      TINHTT:
        params[:TINHTT],

      DTUT:
        params[:DTUT],

      KVUT:
        params[:KVUT],

      NAMTN:
        params[:NAMTN],

      NOIHOC12:
        params[:NOIHOC12],

      THPT:
        params[:THPT],

      SDT:
        params[:SDT],

      EMAIL:
        params[:EMAIL],

      DIACHI:
        params[:DIACHI],

      ANHHOCBA:
        hocba,

      HANHKIEM:
        params[:HANHKIEM],

      KQHT12:
        params[:KQHT12],

      ANHGIAYTOKHAC:
        giaytokhac,

      LOAIDAOTAO:
        params[:LOAIDAOTAO]
    )

    # =========================
    # LƯU ĐIỂM HỌC BẠ
    # CHỈ LƯU MÔN THUỘC 2 TỔ HỢP
    # =========================

    diem_mon = {}
    if params[:DIEM_MON].present?
      diem_mon = JSON.parse(params[:DIEM_MON])
    end

    # danh sách môn cần lưu
    ds_mon_can_luu = []

    # =========================
    # LẤY TỔ HỢP NV1
    # =========================

    if params[:TOHOP_NV1].present?

      tohop1 =
        Tohopmon.find_by(
          TENTOHOP: params[:TOHOP_NV1]
        )

      if tohop1

        ds_mon_can_luu += [
          tohop1.MON1,
          tohop1.MON2,
          tohop1.MON3
        ]

      end
  end

    # =========================
    # LẤY TỔ HỢP NV2
    # =========================

    if params[:TOHOP_NV2].present?

      tohop2 =
        Tohopmon.find_by(
          TENTOHOP: params[:TOHOP_NV2]
        )

      if tohop2

        ds_mon_can_luu += [
          tohop2.MON1,
          tohop2.MON2,
          tohop2.MON3
        ]

      end
    end

    # xóa trùng
    ds_mon_can_luu.uniq!

    # map tên môn DB -> input js
    map_mon = {
    "Toán" => "toan",
    "Văn" => "van",
    "Tiếng Anh" => "anh",
    "Lý" => "ly",
    "Hóa" => "hoa",
    "Sinh" => "sinh",
    "Sử" => "su",
    "Địa" => "dia",
    "Tin học" => "tin",
    "GDKT và PL" => "gdkt",
    "GDCD" => "gdcd",
    "Công nghệ công nghiệp" => "cn",
    "Công nghệ nông nghiệp" => "cnn"
  }

    # lưu điểm
    ds_mon_can_luu.each do |ten_mon|

      ma_mon = map_mon[ten_mon]

      next unless ma_mon

      Diemhocba.create(

        IDTHISINH:
          thisinh.IDTHISINH,

        MON:
          ten_mon,

        DIEM:
          diem_mon[ma_mon]
      )
    end

    # =========================
    # TÌM ĐỢT TUYỂN SINH
    # =========================

    dot =
      Dottuyensinh.where(
        "NGAYBATDAU <= ? AND NGAYKETTHUC >= ?",
        Date.today,
        Date.today
      ).first

    if dot.nil?

      redirect_to nophoso_nophoso_path,
      alert: "Không có đợt tuyển sinh!"

      return
    end

    phuong_thuc = Phuongthucxettuyen.find_by(
  TENPHUONGTHUC: params[:phuongthucxettuyen]
  )

  id_phuong_thuc =
    phuong_thuc&.IDPHUONGTHUC

    # =========================
    # LƯU HỒ SƠ NV1
    # =========================

    if params[:nguyenvong1].present?

      Hosodangky.create(

        IDTHISINH:
          thisinh.IDTHISINH,

        IDNGANH:
          params[:nguyenvong1],

        IDDOT:
          dot.IDDOT,

        THUTU:
          1,

        IDPHUONGTHUC:
          id_phuong_thuc
      )
    end

    # =========================
    # LƯU HỒ SƠ NV2
    # =========================

    if params[:nguyenvong2].present?

      Hosodangky.create(

      IDTHISINH:
        thisinh.IDTHISINH,

      IDNGANH:
        params[:nguyenvong2],

      IDDOT:
        dot.IDDOT,

      THUTU:
        2,

      IDPHUONGTHUC:
        id_phuong_thuc
    )

    end

    redirect_to trangchu_index_path,
    notice: "Nộp hồ sơ thành công!"

  end

end