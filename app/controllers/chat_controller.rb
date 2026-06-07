require 'net/http'
require 'uri'
require 'json'

class ChatController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:create]

  GROQ_API_KEY = ENV["GROQ_API_KEY"] # paste key của bạn vào đây
  GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
  GROQ_MODEL   = "llama-3.3-70b-versatile"

  def create
    body     = JSON.parse(request.body.read) rescue {}
    messages = Array(body["messages"])

    user_input = messages.last&.dig("content").to_s.strip
    user_input = "Cho tôi biết về các ngành tuyển sinh tại VLUTE" if user_input.empty?

    nganh  = load_json("data/nganh.json")
    tohop  = load_json("data/tohop.json")
    hint   = semantic_hint(user_input)

    system_prompt = build_system_prompt(nganh, tohop, hint)

    # Giữ tối đa 10 lượt hội thoại gần nhất để tránh vượt context
    history = messages.last(10).map do |m|
      { role: m["role"].to_s, content: m["content"].to_s }
    end

    # Đảm bảo message cuối luôn là user
    unless history.last&.dig(:role) == "user"
      history << { role: "user", content: user_input }
    end

    ai_text = call_groq(system_prompt, history)
    ai_text = fallback(user_input) if ai_text.to_s.strip.empty?

    render json: { content: [{ text: ai_text }] }

  rescue => e
    Rails.logger.error("ChatController#create error: #{e.class} – #{e.message}\n#{e.backtrace.first(5).join("\n")}")
    render json: { content: [{ text: "Xin lỗi, server đang gặp sự cố. Vui lòng thử lại sau." }] }, status: :internal_server_error
  end

  private

  # ─── Groq API ────────────────────────────────────────────────────────────────

  def call_groq(system_prompt, messages)
    uri  = URI(GROQ_URL)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl      = true
    http.open_timeout = 10
    http.read_timeout = 30

    req = Net::HTTP::Post.new(uri)
    req["Content-Type"]  = "application/json"
    req["Authorization"] = "Bearer #{GROQ_API_KEY}"
    req.body = {
      model:       GROQ_MODEL,
      temperature: 0.65,
      max_tokens:  1500,
      messages:    [{ role: "system", content: system_prompt }] + messages
    }.to_json

    res  = http.request(req)
    json = JSON.parse(res.body) rescue {}

    if json["error"]
      Rails.logger.error("GROQ API error: #{json['error']}")
      return nil
    end

    json.dig("choices", 0, "message", "content")&.strip

  rescue => e
    Rails.logger.error("GROQ HTTP error: #{e.class} – #{e.message}")
    nil
  end

  # ─── System Prompt ───────────────────────────────────────────────────────────

  def build_system_prompt(nganh, tohop, hint)

    nganh_text = nganh.map.with_index(1) do |n, i|
      ten = n["ten_nganh"] || n["ten"] || n["name"] || n.values.first
      ma  = n["ma_nganh"] || n["ma"]  || n["code"] || ""
      th = n["to_hop"]&.join(", ") || ""
      "#{i}. #{ten} (#{ma}) | Tổ hợp: #{th}"
    end.join("; ")

    tohop_text = tohop.map do |t|
      ma = t["ma"] || t["code"] || ""
      mon = t["mon"] || t["môn"] || t.values.join(", ")
      "#{ma}: #{mon}"
    end.join(", ")

    hint_section = hint.present? ? "\nGợi ý: #{hint}" : ""

    <<~PROMPT
      Bạn là AI tư vấn tuyển sinh VLUTE. Trả lời cực ngắn, chỉ liệt kê 1–2 ngành phù hợp nhất với sở thích, mỗi ngành chỉ nêu: tên, mã ngành, tổ hợp xét tuyển, 1–2 nghề nghiệp tiêu biểu. Nếu sở thích không trùng ngành, gợi ý ngành gần nhất hoặc có học phần liên quan. Không giải thích dài dòng, không lặp lại thông tin, không bịa.
      #{hint_section}
      Ngành: #{nganh_text}
      Tổ hợp: #{tohop_text}
    PROMPT
  end

  # ─── Semantic Hint ───────────────────────────────────────────────────────────

  def semantic_hint(text)
    t = text.downcase.unicode_normalize rescue text.downcase

    hints = []

    hints << "Nhóm ngành IT: Công nghệ thông tin, Kỹ thuật phần mềm, Trí tuệ nhân tạo, An toàn thông tin" \
      if t.match?(/lập trình|code|coding|phần mềm|it|công nghệ thông tin|web|app|ai|trí tuệ nhân tạo/)

    hints << "Nhóm ngành Kỹ thuật: Điện – Điện tử, Cơ khí, Tự động hóa, Kỹ thuật xây dựng" \
      if t.match?(/điện|cơ khí|kỹ thuật|máy móc|tự động|robot|xây dựng|kiến trúc/)

    hints << "Nhóm ngành Kinh tế: Quản trị kinh doanh, Kế toán, Marketing, Tài chính – Ngân hàng" \
      if t.match?(/kinh doanh|kinh tế|kế toán|tài chính|marketing|bán hàng|quản trị/)

    hints << "Nhóm ngành Ngôn ngữ & Truyền thông: Ngôn ngữ Anh, Truyền thông, Quan hệ công chúng" \
      if t.match?(/giao tiếp|tiếng anh|ngoại ngữ|truyền thông|báo chí|pr/)

    hints << "Nhóm ngành Thiết kế & Sáng tạo: Thiết kế đồ họa, Thiết kế công nghiệp, Mỹ thuật ứng dụng" \
      if t.match?(/thiết kế|vẽ|sáng tạo|đồ họa|nghệ thuật|mỹ thuật/)

    hints << "Nhóm ngành Du lịch & Dịch vụ: Quản trị khách sạn, Hướng dẫn viên du lịch" \
      if t.match?(/du lịch|khách sạn|nhà hàng|nấu ăn|ẩm thực/)

    hints.join("; ")
  end

  # ─── Fallback ────────────────────────────────────────────────────────────────

  def fallback(text)
    t = text.downcase

    case
    when t.match?(/lập trình|code|it|phần mềm|ai/)
      <<~TEXT
        **Định hướng ngành Công nghệ thông tin tại VLUTE**

        Dựa trên sở thích của bạn, các ngành sau rất phù hợp:

        🖥️ **1. Công nghệ thông tin (CNTT)**
        - Tổ hợp: A00, A01, D01
        - Nghề nghiệp: Lập trình viên, Kỹ sư phần mềm, DevOps, Quản trị hệ thống
        - Lương khởi điểm: 10–15 triệu/tháng, senior có thể 30–60 triệu

        🤖 **2. Trí tuệ nhân tạo (AI)**
        - Tổ hợp: A00, A01
        - Nghề nghiệp: AI Engineer, Data Scientist, Machine Learning Engineer
        - Lương khởi điểm: 15–20 triệu, rất hot trong 5–10 năm tới

        🔒 **3. An toàn thông tin**
        - Tổ hợp: A00, A01, D01
        - Nghề nghiệp: Security Analyst, Pentester, CISO
        - Lương: Top ngành IT, 20–50 triệu với kinh nghiệm

        💡 Bạn thích nghiêng về xây dựng sản phẩm (lập trình), phân tích dữ liệu hay bảo mật hơn?
      TEXT

    when t.match?(/kinh doanh|kinh tế|kế toán|tài chính/)
      <<~TEXT
        **Định hướng ngành Kinh tế – Quản trị tại VLUTE**

        🏢 **1. Quản trị kinh doanh**
        - Tổ hợp: A00, A01, D01, C00
        - Nghề nghiệp: Quản lý doanh nghiệp, Giám đốc điều hành, Chuyên viên phát triển kinh doanh
        - Lương: 8–20 triệu tùy vị trí và năng lực

        📊 **2. Kế toán – Kiểm toán**
        - Tổ hợp: A00, A01, D01
        - Nghề nghiệp: Kế toán viên, Kiểm toán viên, Giám đốc tài chính (CFO)
        - Lương: 7–15 triệu khởi điểm, CFO 50+ triệu

        📣 **3. Marketing**
        - Tổ hợp: A00, D01, C00
        - Nghề nghiệp: Digital Marketer, Brand Manager, Content Strategist
        - Lương: 8–25 triệu, freelance không giới hạn

        💡 Bạn muốn làm việc thiên về con số (kế toán/tài chính) hay sáng tạo và kinh doanh (marketing/quản trị)?
      TEXT

    else
      <<~TEXT
        Xin chào! Mình là AI tư vấn tuyển sinh của **Trường Đại học Sư Phạm Kỹ Thuật Vĩnh Long(VLUTE)** 🎓

        VLUTE có nhiều nhóm ngành đào tạo chất lượng:
        - 💻 **Công nghệ thông tin & AI** – Lập trình, Trí tuệ nhân tạo, An toàn thông tin
        - ⚙️ **Kỹ thuật** – Điện – Điện tử, Cơ khí, Tự động hóa
        - 📊 **Kinh tế** – Quản trị, Kế toán, Marketing, Tài chính
        - 🎨 **Thiết kế** – Đồ họa, Thiết kế công nghiệp
        - 🌍 **Ngôn ngữ & Du lịch** – Tiếng Anh, Quản trị khách sạn

        Để tư vấn chính xác hơn, bạn có thể chia sẻ:
        - Bạn thích làm gì trong thời gian rảnh?
        - Môn học nào bạn học tốt nhất?
        - Bạn muốn làm nghề gì sau khi ra trường?
      TEXT
    end
  end

  def load_json(path)
    full = Rails.root.join(path)
  # ─── Helpers ────────────────────────────────────────
    return [] unless File.exist?(full)
    JSON.parse(File.read(full, encoding: "UTF-8"))
  rescue JSON::ParserError => e
    Rails.logger.warn("load_json failed for #{path}: #{e.message}")
    []
  end
end