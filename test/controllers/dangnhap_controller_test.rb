require "test_helper"

class DangnhapControllerTest < ActionDispatch::IntegrationTest
  test "should get dangnhap" do
    get dangnhap_dangnhap_url
    assert_response :success
  end
end
