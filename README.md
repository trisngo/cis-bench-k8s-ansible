# CIS BENCH K8S ANSIBLE

## Usage

1. Sao chép main.conf.default sang một file cấu hình mới, đặt tên là main.conf. Sửa chữa nội dung như sau cho phù hợp:

    ```ini
    [web_server]
    host=0.0.0.0
    port=9000

    [DEFAULT]
    default=/home/trind/ansible-projects
    aks_ssh=%(default)s/cis-bench-k8s-ansible/CISBenchApp/script/az-aks-ssh.sh

    [logging]
    dir=%(default)s/cis-bench-k8s-ansible/CISBenchApp/logs
    playbook_dir=%(default)s/cis-bench-k8s-ansible/CISBenchApp/logs/playbook_logs

    [data_store]
    dir=%(default)s/cis-bench-k8s-ansible/CISBenchApp/upload

    [ansible]
    bin=/home/trind/.local/bin/ansible-playbook
    inventory=%(default)s/cis-bench-k8s-ansible/ansible/inventory/hosts

    [minikube]
    bench=%(default)s/cis-bench-k8s-ansible/ansible/minikube_benchmark.yml
    config=%(default)s/cis-bench-k8s-ansible/ansible/minikube_hardening.yml
    result_dir=%(default)s/cis-bench-k8s-ansible/CISBenchApp/application/templates/result/minikube

    [aks]
    bench=%(default)s/cis-bench-k8s-ansible/ansible/aks_benchmark.yml
    config=%(default)s/cis-bench-k8s-ansible/ansible/aks_hardening.yml
    result_dir=%(default)s/cis-bench-k8s-ansible/CISBenchApp/application/templates/result/aks
    ```

    - Mục `default` sửa thành đường dẫn chứa thư mục chứa source code vừa clone.
    - Mục `bin` ở phần `[ansible]` sửa thành đường dẫn của binary `ansible-playbook`

2. Sửa giá trị biến `report_default_path` của file `minikube_benchmark.yml` thành đường dẫn chứa kết quả của ứng dụng CISBenchApp. Là giá trị nằm ở `result_dir` ở phần `[minikube]` tại file `main.conf`.
3. Sửa giá trị biến `report_default_path` của file `aks_benchmark.yml` thành đường dẫn chứa kết quả của ứng dụng CISBenchApp. Là giá trị nằm ở `result_dir` ở phần `[aks]` tại file `main.conf`.
