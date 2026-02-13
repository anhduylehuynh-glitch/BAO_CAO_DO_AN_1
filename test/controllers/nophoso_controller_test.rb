require "test_helper"

class NophosoControllerTest < ActionDispatch::IntegrationTest
  test "should get nophoso" do
    get nophoso_nophoso_url
    assert_response :success
  end
end
