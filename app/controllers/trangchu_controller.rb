class TrangchuController < ApplicationController
  def index
    @tintucs_moinhat = Tintuc.order(NGAYDANG: :desc).limit(4)
  end
end
