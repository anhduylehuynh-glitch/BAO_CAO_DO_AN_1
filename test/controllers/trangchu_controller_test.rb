require "test_helper"

class TrangchuControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get trangchu_index_url
    assert_response :success
  end
end
